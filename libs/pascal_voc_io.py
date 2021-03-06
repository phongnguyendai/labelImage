#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs

XML_EXT = '.xml'
ENCODE_METHOD = 'utf-8'

class PascalVocWriter:

    def __init__(self, foldername, filename, imgSize,databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding=ENCODE_METHOD).replace("  ".encode(), "\t".encode())
        # minidom does not support UTF-8
        '''reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding=ENCODE_METHOD)'''

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None:
            return None

        top = Element('annotation')
        if self.verified:
            top.set('verified', 'yes')

        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        if self.localImgPath is not None:
            localImgPath = SubElement(top, 'path')
            localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)


    def addBndBox_2(self, xmin, ymin, xmax, ymax, xmid, ymid, list_points, name, difficult, kind): # list_point : 5 points
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax, 'xmid':xmid,'ymid':ymid,
                  'x0': list_points[0][0], 'y0': list_points[0][1],
                  'x1': list_points[1][0], 'y1': list_points[1][1],
                  'x2': list_points[2][0], 'y2': list_points[2][1],
                  'x3': list_points[3][0], 'y3': list_points[3][1]}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        bndbox['kind'] = kind #kind = vertical or horizontal
        self.boxlist.append(bndbox)

    def appendObjects(self, top):
        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            try:
                name.text = unicode(each_object['name'])
            except NameError:
                # Py3: NameError: name 'unicode' is not defined
                name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(each_object['ymax']) == int(self.imgSize[0]) or (int(each_object['ymin'])== 1):
                truncated.text = "1" # max == height or min
            elif (int(each_object['xmax'])==int(self.imgSize[1])) or (int(each_object['xmin'])== 1):
                truncated.text = "1" # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str( bool(each_object['difficult']) & 1 )
            kind = SubElement(object_item, 'kind')
            kind.text = str(each_object["kind"])

            bndbox = SubElement(object_item, 'bndbox')

            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(each_object['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(each_object['ymin'])


            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(each_object['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(each_object['ymax'])
            xmid = SubElement(bndbox, 'xmid')
            xmid.text = str(each_object['xmid'])
            ymid = SubElement(bndbox, 'ymid')
            ymid.text = str(each_object['ymid'])

            x0 = SubElement(bndbox, 'x0')
            x0.text = str(each_object['x0'])
            y0 = SubElement(bndbox, 'y0')
            y0.text = str(each_object['y0'])

            x1 = SubElement(bndbox, 'x1')
            x1.text = str(each_object['x1'])
            y1 = SubElement(bndbox, 'y1')
            y1.text = str(each_object['y1'])

            x2 =   SubElement(bndbox, 'x2')
            x2.text = str(each_object['x2'])
            y2 =   SubElement(bndbox, 'y2')
            y2.text = str(each_object['y2'])

            x3 =   SubElement(bndbox, 'x3')
            x3.text = str(each_object['x3'])
            y3 =   SubElement(bndbox, 'y3')
            y3.text = str(each_object['y3'])





    def save(self, targetFile=None):
        root = self.genXML()
        self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding=ENCODE_METHOD)
        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()


class PascalVocReader:

    def __init__(self, filepath):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath
        self.verified = False
        try:
            self.parseXML()
        except:
            pass

    def getShapes(self):
        return self.shapes

    def addShape(self, label, bndbox, difficult):
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        xmid = int(bndbox.find('xmid').text)
        ymid = int(bndbox.find('ymid').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmid, ymid)]
        print(points)
        self.shapes.append((label, points, None, None, difficult))

    def addShape_2(self, label, bndbox, difficult):

        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        xmid = int(float(bndbox.find('xmid').text))
        ymid = int(float(bndbox.find('ymid').text))
        x0 = int(float(bndbox.find('x0').text))
        y0 = int(float(bndbox.find('y0').text))
        x1 = int(float(bndbox.find('x1').text))
        y1 = int(float(bndbox.find('y1').text))
        x2 = int(float(bndbox.find('x2').text))
        y2 = int(float(bndbox.find('y2').text))
        x3 = int(float(bndbox.find('x3').text))
        y3 = int(float(bndbox.find('y3').text))

        # points1 = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmid, ymid)]
        # print("points1: ", points1)
        points = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (xmid, ymid)]
        # print("points:", points)

        self.shapes.append((label, points, None, None, difficult))

    def parseXML(self):
        assert self.filepath.endswith(XML_EXT), "Unsupport file format"
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        filename = xmltree.find('filename').text
        try:
            verified = xmltree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xmltree.findall('object'):
            bndbox = object_iter.find("bndbox")
            label = object_iter.find('name').text
            # Add chris
            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.addShape_2(label, bndbox, difficult)
        return True
