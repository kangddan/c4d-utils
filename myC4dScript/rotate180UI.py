import c4d

#如果关节是Z轴对齐，镜像选择XY轴向，同时更改脚本旋转轴向为Z
#如果关节是X轴对齐，镜像选择YZ轴向,同时更改脚本旋转轴向为X

class Rotate180UI(c4d.gui.GeDialog):
    TEXTID       = 416123
    MAINLAYOUTID = 10086
    COMBOBOXID   = 41915
    ROTATEBUTID  = 1008611

    UI_INSTANCE = None
    @classmethod
    def UIDisplay(cls):
        if cls.UI_INSTANCE is None:
            cls.UI_INSTANCE = Rotate180UI()
        else:
            cls.UI_INSTANCE.Open(dlgtype=c4d.DLG_TYPE_ASYNC)

    def __init__(self, *args, **kwargs):
        super(Rotate180UI, self).__init__(*args, **kwargs)
        self.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=0,
                  xpos=-2, ypos=-2, defaultw=300, defaulth=100, subid=0)

    def CreateLayout(self):
        self.SetTitle('ROTATE 180')
        self.mainLayout(self.createWidget)
        self.GroupEnd()
        return True

    # ---------------------------------------------------------
    def mainLayout(self, widgets):
        self.GroupBegin(self.MAINLAYOUTID, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, cols=0, rows=1, title="",
                        groupflags=c4d.BFV_GRIDGROUP_EQUALCOLS, initw=0, inith=0)
        widgets()

    def createWidget(self):
        self.AddStaticText(self.TEXTID, flags=c4d.BFH_LEFT, name='Axis:')
        self.AddComboBox(self.COMBOBOXID, flags=c4d.BFH_SCALEFIT, initw=80, inith=15)

        self.AddChild(self.COMBOBOXID, 0, 'Rotate X')
        self.AddChild(self.COMBOBOXID, 1, 'Rotate Y')
        self.AddChild(self.COMBOBOXID, 2, 'Rotate Z')

        self.rotateBut = self.AddButton(self.ROTATEBUTID, flags=c4d.BFH_SCALEFIT, initw=100 ,inith=20 ,name='Go!')

    def Command(self, _id, message):
        if _id == self.ROTATEBUTID:
            index = self.GetInt32(self.COMBOBOXID)
            self.rotate180(index)

        return True

    # ---------------------------------------------------------
    @staticmethod
    def rotate180(axis):
        sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        if not sel: return

        axisMap = {0: c4d.utils.MatrixRotX(c4d.utils.DegToRad(180)),
                   1: c4d.utils.MatrixRotY(c4d.utils.DegToRad(180)),
                   2: c4d.utils.MatrixRotZ(c4d.utils.DegToRad(180))}

        doc.StartUndo()
        for obj in sel:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            baseMatrix = obj.GetMg()
            obj.SetMg(baseMatrix * axisMap[axis])
            newMatrix = obj.GetMg()
            for child in obj.GetChildren():
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, child)
                child.SetMg(baseMatrix * ~newMatrix * child.GetMg())

            if isinstance(obj, (c4d.SplineObject, c4d.PolygonObject)):
                points = obj.GetAllPoints()
                for p in range(len(points)):
                    obj.SetPoint(p, ~baseMatrix * newMatrix * points[p])
                obj.Message(c4d.MSG_UPDATE)

        doc.EndUndo()
        c4d.EventAdd()

if __name__ == '__main__':
    Rotate180UI.UIDisplay()

'''
Revision History
Revision 1: 2024-07-13 : First publish

code by kangddan
https://github.com/kangddan
https://animator.at8.fun/
https://space.bilibili.com/174575687
https://x.com/kangddan1
'''