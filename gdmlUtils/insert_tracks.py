from FreeCAD import Vector
import Part
from Part import makeBox, makeCone, makeCylinder, makePolygon
import math
import FreeCAD, FreeCADGui
from PySide import QtGui, QtCore
import os
from pivy import coin

primary_track_color = (0.0/255, 1.0, 1.0)
scattered_track_color = (1.0, .0, .0)

path_to_ui = os.environ['HOME']+'/.FreeCAD/Macro/tracks_viewer.ui'


class TracksViewer:
    def __init__(self):
        print(f'Curdir {os.curdir}')
        self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)
        intValidator = QtGui.QIntValidator()
        intValidator.setBottom(1)
        self.form.maxIDLineEdit.setValidator(intValidator)
        self.max_primary_id = 1000
        self.form.maxIDLineEdit.setText(str(self.max_primary_id))
        self.form.fileButton.clicked.connect(self.openFile)

        self.form.maxIDLineEdit.returnPressed.connect(self.changeMaxID)
        doc = App.ActiveDocument
        self.zScreen = 0
        self.xmin = -500
        self.xmax = 500
        self.ymin = -500
        self.ymax = 500
        self.zmin = 0
        self.zmax = 1000
        screenPlane = doc.addObject("Part::Plane", "screen")
        screenPlane.Length = 2*(self.xmax - self.xmin)
        screenPlane.Width = 2*(self.ymax - self.ymin)
        screenPlane.Placement = App.Placement(
            App.Vector(-screenPlane.Length/2, -screenPlane.Length/2, self.zScreen),
            App.Rotation(0, 0, 0))

        self.form.screenCheckBox.setChecked(True)
        self.form.screenCheckBox.stateChanged.connect(self.screenToggled)
        self.form.zScreenSpinBox.setRange(self.zmin, self.zmax)
        self.form.zScreenSpinBox.setSingleStep(10)
        self.form.zScreenSpinBox.valueChanged.connect(self.zScreenChanged)

        self.form.hideTracksCheckBox.stateChanged.connect(self.hideTracksToggled)
        self.form.filterOnScreenCheckBox.stateChanged.connect(self.gateTracks)

        self.tracks = []
        pointsGroup = doc.addObject("App::DocumentObjectGroup", "screenPoints")
        tracksGroup = doc.addObject("App::DocumentObjectGroup", "tracks")

        self.selecting = False

    def gateTracks(self, i):
        view = FreeCADGui.activeDocument().activeView()
        if self.form.filterOnScreenCheckBox.isChecked():
            self.mouseObserver = view.addEventCallback("SoButtonEvent", self.mouseButtonEvent)
        else:
            view.removeEventCallback("SoButtonEvent", self.mouseObserver)

    def mouseButtonEvent(self, info):
        doc = App.ActiveDocument
        if info["State"] == "DOWN":
            self.selecting = True
        if self.selecting is True and info["State"] == "UP":
            self.selecting = False
            sel = FreeCADGui.Selection.getSelection()
            tracksGroup = doc.getObject("tracks")
            tracksGroup.Visibility = False
            for obj in tracksGroup.OutList:
                obj.Visibility = False

            for obj in sel:
                if obj.TypeId == 'Part::Feature' and obj.Name[:5] == 'point':
                    ID = obj.Name[6:]
                    track = doc.getObject("track_"+ID)
                    if track is not None:
                        track.Visibility = True

    def hideTracksToggled(self, i):
        doc = App.ActiveDocument
        tracksGroup = doc.getObject("tracks")
        if self.form.hideTracksCheckBox.isChecked():
            tracksGroup.Visibility = False
        else:
            tracksGroup.Visibility = True

    def setScreen(self):
        doc = App.ActiveDocument
        screenPlane = doc.getObject("screen")
        screenPlane.Length = 2*(self.xmax - self.xmin)
        screenPlane.Width = 2*(self.ymax - self.ymin)
        base = screenPlane.Placement.Base
        base.x = -screenPlane.Length/2
        base.y = -screenPlane.Width/2
        screenPlane.Placement.Base = base
        self.form.zScreenSpinBox.setRange(self.zmin, self.zmax)

    def zScreenChanged(self, z):
        doc = App.ActiveDocument
        screenPlane = doc.getObject("screen")
        base = screenPlane.Placement.Base
        base.z = z
        screenPlane.Placement.Base = base
        self.zScreen = z
        self.updateScreenPoints()

    def binSearchZ(self, track):
        points = track['points']
        i1 = 0
        i2 = len(points) - 1
        imid = int((i1+i2)/2)
        iold = 0
        while imid != iold:
            if self.zScreen < points[imid].z:
                i2 = imid
            else:
                i1 = imid
            iold = imid
            imid = int((i1+i2)/2)
        return imid
            
        
    def updateScreenPoints(self):
        doc = App.ActiveDocument
        pointsGroup = doc.getObject("screenPoints")

        x2 = 0
        y2 = 0
        avgx = 0
        avgy = 0
        N = 0
        for track in self.tracks:
            ID = track['ID']
            points = track['points']
            ptName = "point_"+str(ID)
            part = doc.getObject(ptName)
            i = self.binSearchZ(track)
            if (i == 0 and points[i].z > self.zScreen) \
               or (i == len(points) - 1 and points[i].z < self.zScreen):
                if part is not None:
                    doc.removeObject(ptName)
                continue
            x = points[i].x
            y = points[i].y
            avgx += x
            avgy += y
            x2 += x*x
            y2 += y*y
            N += 1
            v = Part.Vertex(x, y, self.zScreen)
            if part is None:
                part = doc.addObject("Part::Feature", ptName)
                part.ViewObject.PointColor = (0., 0., 1.0)
                pointsGroup.addObject(part)
            part.Shape = v

        sx = 0
        sy = 0
        if N > 1:
            avgx = avgx/N
            avgy = avgy/N
            sx = math.sqrt(1./N*(x2 - N*avgx*avgx))
            sy = math.sqrt(1./N*(y2 - N*avgy*avgy))
        self.form.sxValue.setText(f'{sx:.3f}')
        self.form.syValue.setText(f'{sy:.3f}')

    def showScreen(self):
        doc = App.ActiveDocument
        screenPart = doc.getObject("screen")
        screenPart.Visibility = True
        self.updateScreenPoints()

    def hideScreen(self):
        doc = App.ActiveDocument
        screenPart = doc.getObject("screen")
        screenPart.Visibility = False

    def screenToggled(self, i):
        if self.form.screenCheckBox.isChecked():
            self.showScreen()
        else:
            self.hideScreen()

    def changeMaxID(self):
        text = self.form.maxIDLineEdit.text()
        self.max_primary_id = int(text)
        self.setTrackColors()

    def openFile(self):
        doc = App.ActiveDocument
        docFile = doc.FileName
        dir = os.path.dirname(docFile)
        fileName = ""
        print("Open File")
        try:
            fileName, Filter = QtGui.QFileDialog.getOpenFileName(
                None, "Read tracks file", dir,
                "Track files (*.txt);;All files(*)")
            if fileName == "":
                App.Console.PrintMessage("Process aborted\n")
                return
            else:
                self.form.fileNameLineEdit.setText(fileName)
                self.insert_tracks(fileName)
                return
        except:
            return

    def read_trajectories(self, fileName):
        trajectories = []
        trajectory = []
        fd = open(fileName, 'r')
        xmin = 1e10
        xmax = -1e10
        ymin = 1e10
        ymax = -1e10
        zmin = 1e10
        zmax = -1e10
        
        for line in fd.readlines():
            words = line.strip().split()
            if len(words) == 0:
                track = {'ID': ID, 'points': trajectory}
                trajectories.append(track)
                continue
            if words[0] == "ID":
                skip_next = True
                ID = int(float(words[1]))
                trajectory = []
                continue
            if skip_next:
                skip_next = False
                continue
            else:
                x = float(words[0])*1000
                y = float(words[1])*1000
                z = float(words[2])*1000
                xmin = min(x, xmin)
                xmax = max(x, xmax)
                ymin = min(y, ymin)
                ymax = max(y, ymax)
                zmin = min(z, zmin)
                zmax = max(z, zmax)
                trajectory.append(Vector(x, y, z))

        fd.close()
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        return trajectories

    def insert_tracks(self, fileName):
        self.tracks = self.read_trajectories(fileName)
        doc = App.ActiveDocument
        tracksGroup = doc.getObject("tracks")
        for track in tracksGroup.OutList:
            doc.removeObject(track.Name)
        screenGroup = doc.getObject("screenPoints")
        for pt in screenGroup.OutList:
            doc.removeObject(pt.Name)
            
        for track in self.tracks:
            ID = track['ID']
            points = track['points']
            if len(points) < 2:
                continue
            pol = makePolygon(points)
            part = doc.addObject("Part::Feature", "track_"+str(ID))
            part.Shape = pol
            tracksGroup.addObject(part)
        self.setTrackColors()
        self.setScreen()
        if self.form.screenCheckBox.isChecked():
            self.showScreen()

    def setTrackColors(self):
        tracksGroup = App.ActiveDocument.getObject("tracks")
        for part in tracksGroup.OutList:
            ID = int(part.Name[6:])
            if ID < self.max_primary_id:
                part.ViewObject.LineColor = primary_track_color
                part.ViewObject.PointColor = primary_track_color
            else:
                part.ViewObject.LineColor = scattered_track_color
                part.ViewObject.PointColor = scattered_track_color


panel = TracksViewer()
panel.form.show()
