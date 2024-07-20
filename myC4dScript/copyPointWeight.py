import c4d
from c4d import gui
doc = c4d.documents.GetActiveDocument()

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
        if not isinstance(obj, c4d.PolygonObject):
            c4d.gui.MessageDialog('Please select a polygon object!')
            return True

        weightTag = obj.GetTag(c4d.Tweights)
        if weightTag is None:
            c4d.gui.MessageDialog('The selected object has no weight tag!')
            return True

        if _id == self.COPYBUTID:
            self.weights = []
            _str = self.getSelectedPointWeight(obj, weightTag, self.weights)

            self.SetString(self.TEXTEDITID, _str, tristate=False, flags=0)
            linkBox = self.FindCustomGui(self.LINKBOXID, c4d.CUSTOMGUI_LINKBOX)
            linkBox.SetLink(obj)

        elif _id == self.PASTEBUTID:
            doc.StartUndo()
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            self.setSelectedPointsWeight(obj, weightTag, self.weights)
            c4d.EventAdd()
            doc.EndUndo()
        return True

    # ------------------------------------------------------
    @staticmethod
    def getSelectedPointWeight(obj, weightTag, weightData):
        for p in CopyPointWeightUI.getSelectedPoints(obj):
            for j in range(weightTag.GetJointCount()):
                pointWeight = weightTag.GetWeight(j, p)
                weightData.append(pointWeight)
            return '< {} > : {}'.format('index', p)

    @staticmethod
    def setSelectedPointsWeight(obj, weightTag, weightData):
        for p in CopyPointWeightUI.getSelectedPoints(obj):
            for index, j in enumerate(range(weightTag.GetJointCount())):
                #weightTag.SetWeight(j, p, 0.0)
                weightTag.SetWeight(j, p, weightData[index])
        weightTag.WeightDirty() # update Skin

    @staticmethod
    def _getSelectedPoints(obj):
        return [p for p in range(obj.GetPointCount()) if obj.GetPointS().IsSelected(p)]

    @staticmethod
    def getSelectedPoints(obj):
        bs = obj.GetPointS()
        sel = bs.GetAll(obj.GetPointCount())
        return [index for index, selected in enumerate(sel) if selected]

if __name__=='__main__':
    CopyPointWeightUI.UIDisplay()

"""
code by kangddan
Revision History
Revision 1: 2024-04-23 : First publish
"""