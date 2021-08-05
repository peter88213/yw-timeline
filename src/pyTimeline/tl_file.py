"""Provide a Timeline project file representation.

Part of the yw-timeline project (https://github.com/peter88213/yw-timeline)
Copyright (c) 2021 Peter Triesberger
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
import xml.etree.ElementTree as ET

from datetime import datetime
from datetime import timedelta

from pywriter.model.novel import Novel
from pywriter.model.chapter import Chapter
from pyTimeline.scene_event import SceneEvent
from pyTimeline.item_event import ItemEvent

DIRTY_FIX_TIME = '2021-10-01 11:11:11'
# This is used to provisionally create a time interval if needed.
# To be removed as soon as better time calculation methods are available.


class TlFile(Novel):
    """Timeline project file representation.

    This class represents a file containing a timeline with additional 
    attributes and structural information (a full set or a subset
    of the information included in an Timeline project file).
    """

    DESCRIPTION = 'Timeline'
    EXTENSION = '.timeline'
    SUFFIX = None
    # To be extended by file format specific subclasses.

    def __init__(self, filePath, **kwargs):
        Novel.__init__(self, filePath, **kwargs)
        self.tree = None
        self.sceneMarker = kwargs['scene_label']
        self.itemMarker = kwargs['item_category']
        self.defaultDateTime = kwargs['default_date_time']
        self.sceneColor = kwargs['scene_color']
        self.itemColor = kwargs['item_color']
        self.ignoreItems = kwargs['ignore_items']
        self.ignoreUnspecific = kwargs['ignore_unspecific']

    def convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        """
        if text is not None:

            if text.startswith(' ('):
                text = text.lstrip()

            elif text.startswith(' ['):
                text = text.lstrip()

        return text

    def convert_from_yw(self, text):
        """Return text, converted from yw7 markup to target format.
        """
        if text is not None:

            if text.startswith('('):
                text = ' ' + text

            elif text.startswith('['):
                text = ' ' + text

        return text

    def read(self):
        """Parse the file and store selected properties.
        """
        def remove_contId(event, text):
            """If text comes with a Container ID, remove it 
            and store it in the contId property. 
            """

            if text:
                match = re.match('([\(\[][0-9]+[\)\]])', text)

                if match:
                    contId = match.group()
                    event.contId = contId
                    text = text.split(contId, 1)[1]

            return text

        fileName, fileExtension = os.path.splitext(self.filePath)
        ywFile = fileName + '.yw7'

        if os.path.isfile(ywFile):
            isOutline = False
            doRewrite = False

        else:
            isOutline = True
            doRewrite = True

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        root = self.tree.getroot()

        # Find all itemIDs.

        existingItemIds = []

        for event in root.iter('event'):

            try:
                category = event.find('category').text

                if self.itemMarker in category:
                    labels = event.find('labels').text
                    itemId = re.search('ItemID\:([0-9]+)', labels).group(1)
                    existingItemIds.append(itemId)

            except:
                pass

        sceneCount = 0
        itemCount = 0
        scIdsByDate = {}
        itIdsByDate = {}

        for event in root.iter('event'):
            isScene = False
            isItem = False
            scId = None
            sceneMatch = None
            itemMatch = None
            labels = ''

            if event.find('labels') is not None:
                labels = event.find('labels').text
                itemMatch = re.search('ItemID\:([0-9]+)', labels)
                sceneMatch = re.search('ScID\:([0-9]+)', labels)

            if event.find('category') is not None:
                category = event.find('category').text

                if not self.ignoreItems and self.itemMarker in category:
                    isItem = True
                    itemCount += 1

                    if sceneMatch is not None:
                        labels = labels.replace(sceneMatch.group(), '')
                        event.find('labels').text = labels
                        doRewrite = True

                elif sceneMatch is not None:
                    isScene = True
                    sceneCount += 1
                    sceneMarker = sceneMatch.group()

            elif not self.ignoreItems and itemMatch is not None:
                labels = labels.replace(itemMatch.group(), '')
                event.find('labels').text = labels
                doRewrite = True

            elif sceneMatch is not None:
                isScene = True
                sceneCount += 1
                sceneMarker = sceneMatch.group()

            else:
                continue

            if isOutline:

                if self.sceneMarker in labels:
                    sceneMarker = self.sceneMarker
                    isScene = True
                    sceneCount += 1

                elif isItem:
                    itId = str(itemCount)
                    self.items[itId] = ItemEvent()

                    if event.find('labels') is None:
                        label = ET.Element('labels')
                        label.text = 'ItemID:' + itId
                        event.insert(9, label)

                    else:
                        event.find('labels').text = 'ItemID:' + itId

                if isScene:
                    scId = str(sceneCount)
                    event.find('labels').text = labels.replace(sceneMarker, 'ScID:' + scId)
                    self.scenes[scId] = SceneEvent()
                    self.scenes[scId].status = 1
                    # Set scene status = "Outline".

            elif isScene:

                try:
                    scId = sceneMatch.group(1)
                    self.scenes[scId] = SceneEvent()

                except:
                    continue

            elif isItem:

                try:
                    itId = itemMatch.group(1)

                except:
                    i = itemCount

                    while str(i) in existingItemIds:
                        i += 1

                    itId = str(i)
                    existingItemIds.append(itId)

                    if event.find('labels') is None:
                        label = ET.Element('labels')
                        label.text = 'ItemID:' + itId
                        event.insert(9, label)

                    doRewrite = True

                self.items[itId] = ItemEvent()

            if isItem:

                try:
                    title = event.find('text').text
                    title = remove_contId(self.items[itId], title)
                    title = self.convert_to_yw(title)
                    self.items[itId].title = title

                except:
                    self.items[itId].title = self.itemMarker + ' ' + itId

                try:
                    self.items[itId].desc = event.find('description').text

                except:
                    pass

                try:
                    startDateTime = event.find('start').text

                    if not startDateTime in itIdsByDate:
                        itIdsByDate[startDateTime] = []

                    itIdsByDate[startDateTime].append(itId)

                except:
                    pass

            elif isScene:

                try:
                    title = event.find('text').text
                    title = remove_contId(self.scenes[scId], title)
                    title = self.convert_to_yw(title)
                    self.scenes[scId].title = title

                except:
                    self.scenes[scId].title = 'Scene ' + scId

                try:
                    self.scenes[scId].desc = event.find('description').text

                except:
                    pass

                #--- Process start date/time.

                dtIsValid = True
                # The date/time combination is within the range yWriter can process.

                try:
                    startDateTime = event.find('start').text
                    endDateTime = event.find('end').text

                    if not startDateTime in scIdsByDate:
                        scIdsByDate[startDateTime] = []

                    scIdsByDate[startDateTime].append(scId)
                    dt = startDateTime.split(' ')

                    # Prevent two-figure years from becoming "completed" by yWriter.

                    if dt[0].startswith('-'):
                        startYear = -1 * int(dt[0].split('-')[1])
                        self.scenes[scId].endDateTime = endDateTime
                        dtIsValid = False

                    else:
                        startYear = int(dt[0].split('-')[0])

                    if startYear < 100:
                        self.scenes[scId].date = '-0001-01-01'
                        self.scenes[scId].time = '00:00:00'
                        self.scenes[scId].startDate = dt[0]
                        self.scenes[scId].startTime = dt[1]
                        self.scenes[scId].endDateTime = endDateTime
                        dtIsValid = False

                    else:
                        self.scenes[scId].date = dt[0]
                        self.scenes[scId].time = dt[1]

                except:
                    dtIsValid = False

                try:

                    if dtIsValid:

                        #--- Calculate scene duration.

                        startYear = int(dt[0].split('-')[0])
                        startMonth = int(dt[0].split('-')[1])
                        startDay = int(dt[0].split('-')[2])
                        startHour = int(dt[1].split(':')[0])
                        startMinute = int(dt[1].split(':')[1])

                        sceneStart = datetime(startYear, startMonth, startDay, hour=startHour, minute=startMinute)

                        endDate, endTime = endDateTime.split(' ')
                        endYear = int(endDate.split('-')[0])
                        endMonth = int(endDate.split('-')[1])
                        endDay = int(endDate.split('-')[2])
                        endHour = int(endTime.split(':')[0])
                        endMinute = int(endTime.split(':')[1])

                        sceneEnd = datetime(endYear, endMonth, endDay, hour=endHour, minute=endMinute)

                        sceneDuration = sceneEnd - sceneStart
                        self.scenes[scId].lastsDays = str(sceneDuration.days)
                        lastsHours = sceneDuration.seconds // 3600
                        lastsMinutes = (sceneDuration.seconds % 3600) // 60
                        self.scenes[scId].lastsHours = str(lastsHours)
                        self.scenes[scId].lastsMinutes = str(lastsMinutes)
                except:
                    pass

        # Sort items by date/time

        srtItems = sorted(itIdsByDate.items())

        for dt, itList in srtItems:

            for itId in itList:
                self.srtItems.append(itId)

        # Sort scenes by date/time

        srtScenes = sorted(scIdsByDate.items())

        if isOutline:

            # Create a single chapter and assign all scenes to it.

            chId = '1'
            self.chapters[chId] = Chapter()
            self.chapters[chId].title = 'Chapter 1'
            self.srtChapters = [chId]

            for dt, scList in srtScenes:

                for scId in scList:
                    self.chapters[chId].srtScenes.append(scId)

        if doRewrite:

            # Rewrite the timeline with item/scene IDs inserted.

            try:
                self.tree.write(self.filePath, xml_declaration=True, encoding='utf-8')

            except(PermissionError):
                return 'ERROR: "' + os.path.normpath(self.filePath) + '" is write protected.'

        return 'SUCCESS: Timeline read in.'

    def merge(self, source):
        """Copy required attributes of the timeline object.
        """
        def add_contId(event, text):
            """If event has a container ID, add it to text. 
            """

            if event.contId is not None:
                return event.contId + text

            return text

        if self.file_exists():
            message = self.read()
            # initialize data

            if message.startswith('ERROR'):
                return message

        self.chapters = {}
        self.srtChapters = []

        for chId in source.srtChapters:
            self.chapters[chId] = Chapter()
            self.srtChapters.append(chId)

            for scId in source.chapters[chId].srtScenes:

                if self.ignoreUnspecific and source.scenes[scId].date is None and source.scenes[scId].time is None:
                    # Skip scenes with unspecific date/time stamps.
                    continue

                if not scId in self.scenes:
                    self.scenes[scId] = SceneEvent()

                self.chapters[chId].srtScenes.append(scId)

                if source.scenes[scId].title:
                    title = source.scenes[scId].title
                    title = self.convert_from_yw(title)
                    title = add_contId(self.scenes[scId], title)
                    self.scenes[scId].title = title

                self.scenes[scId].desc = source.scenes[scId].desc

                if source.scenes[scId].date is not None and source.scenes[scId].date != '0001-01-01':

                    # The date is not "BC", so synchronize it.

                    self.scenes[scId].date = source.scenes[scId].date

                    if source.scenes[scId].time:
                        self.scenes[scId].time = source.scenes[scId].time

                    else:
                        self.scenes[scId].time = '00:00:00'

                    if source.scenes[scId].lastsMinutes is not None:
                        self.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes

                    if source.scenes[scId].lastsHours is not None:
                        self.scenes[scId].lastsHours = source.scenes[scId].lastsHours

                    if source.scenes[scId].lastsDays is not None:
                        self.scenes[scId].lastsDays = source.scenes[scId].lastsDays

                elif self.scenes[scId].startDate is not None:

                    # Restore two-figure year.

                    self.scenes[scId].date = self.scenes[scId].startDate
                    self.scenes[scId].time = self.scenes[scId].startTime

                self.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene
                self.scenes[scId].isUnused = source.scenes[scId].isUnused
                self.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene

        scenes = list(self.scenes)

        for scId in scenes:

            if not scId in source.scenes:
                del self.scenes[scId]

        for itId in source.srtItems:

            if not itId in self.items:
                self.items[itId] = ItemEvent()

            if source.items[itId].title:
                title = source.items[itId].title
                title = self.convert_from_yw(title)
                title = add_contId(self.items[itId], title)
                self.items[itId].title = title

            self.items[itId].desc = source.items[itId].desc

        items = list(self.items)

        for itId in items:

            if not itId in source.items:
                del self.items[itId]

        self.srtItems = list(self.items)

        return 'SUCCESS'

    def write(self):
        """Write selected properties to the file.
        """

        def build_item_subtree(xmlEvent, itId, dtMin, dtMax):
            item = self.items[itId]
            scIndex = 0

            if xmlEvent.find('start') is None:
                ET.SubElement(xmlEvent, 'start').text = self.defaultDateTime

            scIndex += 1

            if xmlEvent.find('end') is None:
                ET.SubElement(xmlEvent, 'end').text = self.defaultDateTime

            scIndex += 1

            if not item.title:
                item.title = 'Unnamed item ID' + itId

            try:
                xmlEvent.find('text').text = item.title

            except(AttributeError):
                ET.SubElement(xmlEvent, 'text').text = item.title

            scIndex += 1

            if xmlEvent.find('progress') is None:
                ET.SubElement(xmlEvent, 'progress').text = '0'

            scIndex += 1

            if xmlEvent.find('fuzzy') is None:
                ET.SubElement(xmlEvent, 'fuzzy').text = 'False'

            scIndex += 1

            if xmlEvent.find('locked') is None:
                ET.SubElement(xmlEvent, 'locked').text = 'False'

            scIndex += 1

            if xmlEvent.find('ends_today') is None:
                ET.SubElement(xmlEvent, 'ends_today').text = 'False'

            scIndex += 1

            try:
                xmlEvent.find('category').text = self.itemMarker

            except:
                ET.SubElement(xmlEvent, 'category').text = self.itemMarker

            scIndex += 1

            if item.desc is not None:

                try:
                    xmlEvent.find('description').text = item.desc

                except(AttributeError):

                    if xmlEvent.find('labels') is None:

                        # Append the description.

                        ET.SubElement(xmlEvent, 'description').text = item.desc

                    else:
                        # Insert the description.

                        desc = ET.Element('description')
                        desc.text = item.desc
                        xmlEvent.insert(scIndex, desc)

            elif xmlEvent.find('description') is not None:
                xmlEvent.remove(xmlEvent.find('description'))

            if xmlEvent.find('labels') is None:
                ET.SubElement(xmlEvent, 'labels').text = 'ItemID:' + itId

            if xmlEvent.find('default_color') is None:
                ET.SubElement(xmlEvent, 'default_color').text = '192,192,192'

            if self.defaultDateTime < dtMin:
                dtMin = self.defaultDateTime

            if self.defaultDateTime > dtMax:
                dtMax = self.defaultDateTime

            return dtMin, dtMax

        def build_event_subtree(xmlEvent, scId, dtMin, dtMax):
            scene = self.scenes[scId]
            scIndex = 0

            if scene.date is not None:
                startDateTime = scene.date + ' '

                if not scene.time:
                    startDateTime += '00:00:00'

                else:
                    startDateTime += scene.time

            else:
                startDateTime = self.defaultDateTime

            try:
                xmlEvent.find('start').text = startDateTime

            except(AttributeError):
                ET.SubElement(xmlEvent, 'start').text = startDateTime

            scIndex += 1

            if startDateTime < dtMin:
                dtMin = startDateTime

            #--- Calculate end date from scene duration.

            if scene.lastsDays and scene.lastsHours and scene.lastsMinutes:
                lastsDays = int(scene.lastsDays)
                lastsSeconds = (int(scene.lastsHours) * 3600) + (int(scene.lastsMinutes) * 60)
                sceneDuration = timedelta(days=lastsDays, seconds=lastsSeconds)

                startDate, startTime = startDateTime.split(' ')
                startYear = int(startDate.split('-')[0])
                startMonth = int(startDate.split('-')[1])
                startDay = int(startDate.split('-')[2])
                startHour = int(startTime.split(':')[0])
                startMinute = int(startTime.split(':')[1])
                sceneStart = datetime(startYear, startMonth, startDay, hour=startHour, minute=startMinute)

                sceneEnd = sceneStart + sceneDuration
                endDateTime = sceneEnd.isoformat(' ')

                if startDateTime > endDateTime:
                    endDateTime = startDateTime

            elif scene.endDateTime is not None and scene.endDateTime > startDateTime:
                endDateTime = scene.endDateTime

            else:
                endDateTime = startDateTime

            try:
                xmlEvent.find('end').text = endDateTime

            except(AttributeError):
                ET.SubElement(xmlEvent, 'end').text = endDateTime

            scIndex += 1

            if endDateTime > dtMax:
                dtMax = endDateTime

            if not scene.title:
                scene.title = 'Unnamed scene ID' + scId

            try:
                xmlEvent.find('text').text = scene.title

            except(AttributeError):
                ET.SubElement(xmlEvent, 'text').text = scene.title

            scIndex += 1

            if xmlEvent.find('progress') is None:
                ET.SubElement(xmlEvent, 'progress').text = '0'

            scIndex += 1

            if xmlEvent.find('fuzzy') is None:
                ET.SubElement(xmlEvent, 'fuzzy').text = 'False'

            scIndex += 1

            if xmlEvent.find('locked') is None:
                ET.SubElement(xmlEvent, 'locked').text = 'False'

            scIndex += 1

            if xmlEvent.find('ends_today') is None:
                ET.SubElement(xmlEvent, 'ends_today').text = 'False'

            scIndex += 1

            if scene.desc is not None:

                try:
                    xmlEvent.find('description').text = scene.desc

                except(AttributeError):

                    if xmlEvent.find('labels') is None:

                        # Append the description.

                        ET.SubElement(xmlEvent, 'description').text = scene.desc

                    else:
                        # Insert the description.

                        if xmlEvent.find('category') is not None:
                            scIndex += 1

                        desc = ET.Element('description')
                        desc.text = scene.desc
                        xmlEvent.insert(scIndex, desc)

            elif xmlEvent.find('description') is not None:
                xmlEvent.remove(xmlEvent.find('description'))

            if xmlEvent.find('labels') is None:
                ET.SubElement(xmlEvent, 'labels').text = 'ScID:' + scId

            if xmlEvent.find('default_color') is None:
                ET.SubElement(xmlEvent, 'default_color').text = self.sceneColor

            return dtMin, dtMax

        #--- Begin write method

        dtMin = self.defaultDateTime
        dtMax = self.defaultDateTime

        # List all scenes to be exported.
        # Note: self.scenes may also contain orphaned ones.

        srtScenes = []

        for chId in self.srtChapters:

            for scId in self.chapters[chId].srtScenes:

                if self.scenes[scId].isNotesScene:
                    continue

                if self.scenes[scId].isUnused:
                    continue

                if self.scenes[scId].isTodoScene:
                    continue

                srtScenes.append(scId)

        if self.tree is not None:

            # Update an existing XML tree.

            root = self.tree.getroot()
            events = root.find('events')
            trash = []
            scIds = []
            itIds = []

            #--- Update events that are assigned to scenes or items.

            for event in events.iter('event'):

                if event.find('labels') is not None:
                    labels = event.find('labels').text
                    itemMatch = re.search('ItemID\:([0-9]+)', labels)
                    sceneMatch = re.search('ScID\:([0-9]+)', labels)

                else:
                    continue

                if not self.ignoreItems and itemMatch is not None:
                    itId = itemMatch.group(1)

                    if itId in self.items:
                        itIds.append(itId)
                        dtMin, dtMax = build_item_subtree(event, itId, dtMin, dtMax)

                    else:
                        trash.append(event)

                elif sceneMatch is not None:
                    scId = sceneMatch.group(1)

                    if scId in srtScenes:
                        scIds.append(scId)
                        dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

                    else:
                        trash.append(event)

            # Add new events.

            for scId in srtScenes:

                if not scId in scIds:
                    event = ET.SubElement(events, 'event')
                    dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

            if not self.ignoreItems:

                for itId in self.items:

                    if not itId in itIds:
                        event = ET.SubElement(events, 'event')
                        dtMin, dtMax = build_item_subtree(event, itId, dtMin, dtMax)

            # Remove events that are assigned to missing scenes.

            for event in trash:
                events.remove(event)

            if not self.ignoreItems:

                # Add "Item" category, if missing.

                hasItemCategory = False
                categories = root.find('categories')

                for cat in categories.iter('category'):

                    if self.itemMarker in cat.find('name').text:
                        hasItemCategory = True
                        break

                if not hasItemCategory:
                    item = ET.SubElement(categories, 'category')
                    ET.SubElement(item, 'name').text = self.itemMarker
                    ET.SubElement(item, 'color').text = self.itemColor
                    ET.SubElement(item, 'progress_color').text = '255,153,153'
                    ET.SubElement(item, 'done_color').text = '255,153,153'
                    ET.SubElement(item, 'font_color').text = '0,0,0'

        else:

            # Create a new XML tree.

            root = ET.Element('timeline')
            ET.SubElement(root, 'version').text = '2.4.0 (3f207fbb63f0 2021-04-07)'
            ET.SubElement(root, 'timetype').text = 'gregoriantime'
            categories = ET.SubElement(root, 'categories')

            if not self.ignoreItems:
                item = ET.SubElement(categories, 'category')
                ET.SubElement(item, 'name').text = self.itemMarker
                ET.SubElement(item, 'color').text = self.itemColor
                ET.SubElement(item, 'progress_color').text = '255,153,153'
                ET.SubElement(item, 'done_color').text = '255,153,153'
                ET.SubElement(item, 'font_color').text = '0,0,0'

            events = ET.SubElement(root, 'events')

            for scId in srtScenes:
                event = ET.SubElement(events, 'event')
                dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

            if not self.ignoreItems:

                for itId in self.items:
                    event = ET.SubElement(events, 'event')
                    dtMin, dtMax = build_item_subtree(event, itId, dtMin, dtMax)

            view = ET.SubElement(root, 'view')
            period = ET.SubElement(view, 'displayed_period')

            if dtMin == dtMax:

                if DIRTY_FIX_TIME > dtMax:
                    dtMax = DIRTY_FIX_TIME

                elif DIRTY_FIX_TIME < dtMin:
                    dtMin = DIRTY_FIX_TIME

            ET.SubElement(period, 'start').text = dtMin
            ET.SubElement(period, 'end').text = dtMax

        self.indent_xml(root)
        self.tree = ET.ElementTree(root)

        try:
            self.tree.write(self.filePath, xml_declaration=True, encoding='utf-8')

        except(PermissionError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" is write protected.'

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'

    def indent_xml(self, elem, level=0):
        """xml pretty printer

        Kudos to to Fredrik Lundh. 
        Source: http://effbot.org/zone/element-lib.htm#prettyprint
        """
        i = "\n" + level * "  "

        if len(elem):

            if not elem.text or not elem.text.strip():
                elem.text = i + "  "

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

            for elem in elem:
                self.indent_xml(elem, level + 1)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
