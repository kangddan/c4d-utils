import c4d
from c4d import gui

class GetSelectedPointID(object):

    def __init__(self, obj, modeId):
        self.obj    = obj
        self.modeId = modeId

    def run(self) -> list[int]:
        if self.modeId == c4d.Mpoints:
            return self.pointsToId(self.obj)
        elif self.modeId == c4d.Medges:
            return self.edgesToId(self.obj)
        elif self.modeId == c4d.Mpolygons:
            return self.polysToId(self.obj)
        return []
    
    @staticmethod
    def pointsToId(obj) -> list[int]:
        bs  = obj.GetPointS()
        sel = bs.GetAll(obj.GetPointCount())
        return [index for index, selected in enumerate(sel) if selected]
        
    @staticmethod
    def polysToId(obj) -> set[int]:
        bs  = obj.GetPolygonS()
        sel = bs.GetAll(obj.GetPolygonCount())
        selPolyId = [index for index, selected in enumerate(sel) if selected]

        # ---------------------------------------------------
        polys: list[c4d.CPolygon] = obj.GetAllPolygons()
        selPointsId = set()
        for index in selPolyId:
            poly:c4d.CPolygon = polys[index]
            selPointsId.update([poly.a, poly.b, poly.c, poly.d])
        return selPointsId
        
    @staticmethod
    def edgesToId(obj) -> set[int]:
        selEdge: c4d.BaseSelect   = obj.GetEdgeS()
        polys: list[c4d.CPolygon] = obj.GetAllPolygons()
        
        selectedEdges = set()
        for polyIndex, poly in enumerate(polys):
            edges = [
                (poly.a, poly.b),
                (poly.b, poly.c),
                (poly.c, poly.d if poly.c != poly.d else poly.a),
                (poly.d if poly.c != poly.d else poly.a, poly.a)
            ]
            for edgeIndex, (v1, v2) in enumerate(edges):
                selectionIndex = 4 * polyIndex + edgeIndex
                if selEdge.IsSelected(selectionIndex):
                    selectedEdges.update((v1, v2))
                    
        return selectedEdges

class CopyPointWeightUI(gui.GeDialog):
    MAINLAYOUTID = 41650
    LINKBOXID = 19165
    TEXTEDITID = 41915
    COPYBUTID = 123475
    PASTEBUTID = 16546

    UI_INSTANCE = None
    @classmethod
    def UIDisplay(cls):
        if cls.UI_INSTANCE is None:
            cls.UI_INSTANCE = CopyPointWeightUI()
        else:
            cls.UI_INSTANCE.Open(dlgtype=c4d.DLG_TYPE_ASYNC)

    def __init__(self, *args, **kwargs):
        super(CopyPointWeightUI, self).__init__(*args, **kwargs)
        self.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=0,
                  xpos=-2, ypos=-2, defaultw=300, defaulth=100, subid=0)
        self.weights = []

    def CreateLayout(self):
        self.SetTitle('Copy Point Weight')
        self.mainLayout(self.createWidget)
        self.GroupEnd()
        return True

    # ---------------------------------------------------------

    def mainLayout(self, widgets):
        self.GroupBegin(self.MAINLAYOUTID, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, cols=2, rows=0, title="",
                        groupflags=c4d.BFV_GRIDGROUP_EQUALCOLS, initw=0, inith=0)
        widgets()

    def createWidget(self):
        self.AddCustomGui(self.LINKBOXID, c4d.CUSTOMGUI_LINKBOX, 'Link Object', c4d.BFH_SCALEFIT, 100, 0)
        self.AddEditText(self.TEXTEDITID, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, editflags=0)

        self.copyBut = self.AddButton(self.COPYBUTID, flags=c4d.BFH_SCALEFIT, initw=100 ,inith=30 ,name='Copy')
        self.pasteBut = self.AddButton(self.PASTEBUTID, flags=c4d.BFH_SCALEFIT, initw=100 ,inith=30 ,name='Paste')

    # ---------------------------------------------------------

    def Command(self, _id, message):

        obj = doc.GetActiveObject()
        if not obj.CheckType(c4d.Opoint):
            c4d.gui.MessageDialog('Please select a point object!')
            return True

        weightTag = obj.GetTag(c4d.Tweights)
        if weightTag is None:
            c4d.gui.MessageDialog('The selected object has no weight tag!')
            return True

        if _id == self.COPYBUTID:
            if doc.GetMode() != c4d.Mpoints:
                c4d.gui.MessageDialog('Please copy/paste in point mode!')
                return True
            
            self.weights = []
            _str = self.getSelectedPointWeight(obj, weightTag, self.weights)

            self.SetString(self.TEXTEDITID, _str, tristate=False, flags=0)
            linkBox = self.FindCustomGui(self.LINKBOXID, c4d.CUSTOMGUI_LINKBOX)
            linkBox.SetLink(obj)

        elif _id == self.PASTEBUTID:
            if not doc.IsEditMode():
                c4d.gui.MessageDialog('Please in edit mode!')
                return True
            doc.StartUndo()
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            self.setSelectedPointsWeight(obj, weightTag, self.weights)
            c4d.EventAdd()
            doc.EndUndo()
        return True

    # ------------------------------------------------------
    @staticmethod
    def getSelectedPointWeight(obj, weightTag, weightData):
        for p in GetSelectedPointID(obj, doc.GetMode()).run():
            for j in range(weightTag.GetJointCount()):
                pointWeight = weightTag.GetWeight(j, p)
                weightData.append(pointWeight)
            return '< {} > : {}'.format('index', p)

    @staticmethod
    def setSelectedPointsWeight(obj, weightTag, weightData):
        for p in GetSelectedPointID(obj, doc.GetMode()).run():
            for index, j in enumerate(range(weightTag.GetJointCount())):
                #weightTag.SetWeight(j, p, 0.0)
                weightTag.SetWeight(j, p, weightData[index])
        weightTag.WeightDirty() # update Skin

if __name__=='__main__':
    CopyPointWeightUI.UIDisplay()

"""
code by kangddan
Revision History
Revision 1: 2024-04-23 : First publish
Revision 1: 2024-08-03 : Correctly identify point IDs in point, edge, and polygon modes
"""
