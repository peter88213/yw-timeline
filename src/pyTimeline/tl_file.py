"""Timeline base class

Part of the yw-timeline project (https://github.com/peter88213/yw-timeline)
Copyright (c) 2021 Peter Triesberger
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
import xml.etree.ElementTree as ET

from pywriter.model.novel import Novel
from pywriter.model.scene import Scene
from pywriter.model.world_element import WorldElement
from pywriter.model.chapter import Chapter

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
        self.sceneMarker = kwargs['sceneMarker']
        self.ignoreItems = kwargs['ignoreItems']
        self.itemMarker = kwargs['itemMarker']
        self.defaultDateTime = kwargs['defaultDateTime']
        self.sceneColor = kwargs['sceneColor']
        self.itemColor = kwargs['itemColor']

    def read(self):
        """Parse the file and store selected properties.
        """
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
                    self.items[itId] = WorldElement()

                    if event.find('labels') is None:
                        label = ET.Element('labels')
                        label.text = 'ItemID:' + itId
                        event.insert(9, label)

                    else:
                        event.find('labels').text = 'ItemID:' + itId

                if isScene:
                    scId = str(sceneCount)
                    event.find('labels').text = labels.replace(sceneMarker, 'ScID:' + scId)
                    self.scenes[scId] = Scene()
                    self.scenes[scId].status = 1
                    # Set scene status = "Outline".

            elif isScene:

                try:
                    scId = sceneMatch.group(1)
                    self.scenes[scId] = Scene()

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

                self.items[itId] = WorldElement()

            if isItem:

                try:
                    self.items[itId].title = event.find('text').text

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
                    self.scenes[scId].title = event.find('text').text

                except:
                    self.scenes[scId].title = 'Scene ' + scId

                try:
                    self.scenes[scId].desc = event.find('description').text

                except:
                    pass

                try:
                    startDateTime = event.find('start').text

                    if not startDateTime in scIdsByDate:
                        scIdsByDate[startDateTime] = []

                    scIdsByDate[startDateTime].append(scId)
                    dt = startDateTime.split(' ')
                    self.scenes[scId].date = dt[0]
                    self.scenes[scId].time = dt[1]

                except:
                    pass

                try:
                    endDateTime = event.find('end').text

                    #--- TODO: Calculate scene duration

                except:
                    pass

        # Sort items by date/time

        srtItems = sorted(itIdsByDate.items())

        for date, itList in srtItems:

            for itId in itList:
                self.srtItems.append(itId)

        if isOutline:

            # Create a single chapter and assign all scenes to it.

            chId = '1'
            self.chapters[chId] = Chapter()
            self.chapters[chId].title = 'Chapter 1'
            self.srtChapters = [chId]

            # Sort scenes by date/time

            srtScenes = sorted(scIdsByDate.items())

            for date, scList in srtScenes:

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
        if self.file_exists():
            message = self.read()
            # initialize data

            if message.startswith('ERROR'):
                return message

        self.chapters = source.chapters
        self.srtChapters = source.srtChapters

        for scId in source.scenes:

            if not scId in self.scenes:
                self.scenes[scId] = Scene()

            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = source.scenes[scId].title

            self.scenes[scId].desc = source.scenes[scId].desc

            if source.scenes[scId].date is not None:
                self.scenes[scId].date = source.scenes[scId].date

            if source.scenes[scId].time is not None:
                self.scenes[scId].time = source.scenes[scId].time

            if source.scenes[scId].lastsMinutes is not None:
                self.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes

            if source.scenes[scId].lastsHours is not None:
                self.scenes[scId].lastsHours = source.scenes[scId].lastsHours

            if source.scenes[scId].lastsDays is not None:
                self.scenes[scId].lastsDays = source.scenes[scId].lastsDays

            self.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene
            self.scenes[scId].isUnused = source.scenes[scId].isUnused
            self.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene

        scenes = list(self.scenes)

        for scId in scenes:

            if not scId in source.scenes:
                del self.scenes[scId]

        for itId in source.srtItems:

            if not itId in self.items:
                self.items[itId] = WorldElement()

            if source.items[itId].title:
                self.items[itId].title = source.items[itId].title

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

        def build_item_subtree(xmlEvent, itId):
            item = self.items[itId]
            scIndex = 0

            if xmlEvent.find('start') is None:
                ET.SubElement(xmlEvent, 'start').text = self.defaultDateTime

            scIndex += 1

            if xmlEvent.find('end') is None:
                ET.SubElement(xmlEvent, 'end').text = self.defaultDateTime

            scIndex += 1

            if item.title:

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

        def build_event_subtree(xmlEvent, scId, dtMin, dtMax):
            scene = self.scenes[scId]
            scIndex = 0

            if scene.date is not None:
                startDateTime = scene.date + ' '

                if scene.time is None:
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

            endDateTime = startDateTime

            try:
                xmlEvent.find('end').text = endDateTime

            except(AttributeError):
                ET.SubElement(xmlEvent, 'end').text = endDateTime

            scIndex += 1

            if endDateTime > dtMax:
                dtMax = endDateTime

            if scene.title:

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

        try:
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
                        build_item_subtree(event, itId)

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
                        build_item_subtree(event, itId)

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

        except(AttributeError):

            # Create a new XML tree

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
                    build_item_subtree(event, itId)

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
