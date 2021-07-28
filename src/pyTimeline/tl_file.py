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
        self.defaultDateTime = kwargs['defaultDateTime']

    def read(self):
        """Parse the file and store selected properties.
        """
        fileName, fileExtension = os.path.splitext(self.filePath)
        ywFile = fileName + '.yw7'

        if os.path.isfile(ywFile):
            isOutline = False

        else:
            isOutline = True

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        root = self.tree.getroot()

        sceneCount = 0
        scIdsByDate = {}

        for event in root.iter('event'):
            scId = None

            try:
                labels = event.find('labels').text

            except:
                continue

            if isOutline:
                sceneMarker = self.sceneMarker

                if not sceneMarker in labels:
                    match = re.search('ScID\:([0-9])+', labels)

                    if match is None:
                        continue

                    else:
                        sceneMarker = match.group()

                    if sceneMarker is None:
                        continue

                sceneCount += 1
                scId = str(sceneCount)
                event.find('labels').text = labels.replace(sceneMarker, 'ScID:' + scId)
                self.scenes[scId] = Scene()
                self.scenes[scId].status = 1
                # Set scene status = "Outline".

            else:

                try:
                    scId = re.search('ScID\:([0-9]+)', labels).group(1)
                    self.scenes[scId] = Scene()

                except:
                    continue

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

            # Rewrite the timeline with scene IDs inserted.

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

            if source.scenes[scId].desc is not None:
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

        return 'SUCCESS'

    def write(self):
        """Write selected properties to the file.
        """

        def build_event_subtree(xmlEvent, scId, dtMin, dtMax):
            scene = self.scenes[scId]

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

            if startDateTime < dtMin:
                dtMin = startDateTime

            endDateTime = startDateTime

            try:
                xmlEvent.find('end').text = endDateTime

            except(AttributeError):
                ET.SubElement(xmlEvent, 'end').text = endDateTime

            if endDateTime > dtMax:
                dtMax = endDateTime

            if scene.title:

                try:
                    xmlEvent.find('text').text = scene.title

                except(AttributeError):
                    ET.SubElement(xmlEvent, 'text').text = scene.title

            if xmlEvent.find('progress') is None:
                ET.SubElement(xmlEvent, 'progress').text = '0'

            if xmlEvent.find('fuzzy') is None:
                ET.SubElement(xmlEvent, 'fuzzy').text = 'False'

            if xmlEvent.find('locked') is None:
                ET.SubElement(xmlEvent, 'locked').text = 'False'

            if xmlEvent.find('ends_today') is None:
                ET.SubElement(xmlEvent, 'ends_today').text = 'False'

            if scene.desc is not None:

                try:
                    xmlEvent.find('description').text = scene.desc

                except(AttributeError):
                    ET.SubElement(xmlEvent, 'description').text = scene.desc

            if xmlEvent.find('labels') is None:
                ET.SubElement(xmlEvent, 'labels').text = 'ScID:' + scId

            if xmlEvent.find('default_color') is None:
                ET.SubElement(xmlEvent, 'default_color').text = '192,192,192'

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

            # Update events that are assigned to scenes.

            for event in events.iter('event'):

                try:
                    labels = event.find('labels').text
                    scId = re.search('ScID\:([0-9]+)', labels).group(1)

                except:
                    continue

                if scId is None:
                    continue

                if not scId in srtScenes:
                    trash.append(event)
                    continue

                scIds.append(scId)
                dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

            # Add new events.

            for scId in srtScenes:

                if not scId in scIds:
                    event = ET.SubElement(events, 'event')
                    dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

            # Remove events that are assigned to missing scenes.

            for event in trash:
                events.remove(event)

        except(AttributeError):

            # Create a new XML tree

            root = ET.Element('timeline')
            ET.SubElement(root, 'version').text = '2.4.0 (3f207fbb63f0 2021-04-07)'
            ET.SubElement(root, 'timetype').text = 'gregoriantime'
            ET.SubElement(root, 'categories')
            events = ET.SubElement(root, 'events')

            for scId in srtScenes:
                event = ET.SubElement(events, 'event')
                dtMin, dtMax = build_event_subtree(event, scId, dtMin, dtMax)

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
