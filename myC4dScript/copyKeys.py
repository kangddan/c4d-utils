import c4d

def copyAni(noAniObj, aniObj):
    tracks = aniObj.GetCTracks()
    if not tracks:
        return 0

    for track in tracks:
        did = track.GetDescriptionID()
        foundTrack = noAniObj.FindCTrack(did)
        if foundTrack:
            doc.AddUndo(c4d.UNDOTYPE_DELETE, foundTrack)
            foundTrack.Remove()
        clone = track.GetClone()
        noAniObj.InsertTrackSorted(clone)
        doc.AddUndo(c4d.UNDOTYPE_NEW, clone)
    animateflag = c4d.ANIMATEFLAGS_NONE if c4d.GetC4DVersion() > 20000 else c4d.ANIMATEFLAGS_0
    doc.AnimateObject(noAniObj, doc.GetTime(), animateflag)
    return 1

def getAllChildren(obj, children=None):
    if children is None:
        children = []
    child = obj.GetDown()
    while child:
        children.append(child)
        getAllChildren(child, children)
        child = child.GetNext()
    return children

def getObjectsByName(objects):
    objDict = {}
    for obj in objects:
        objDict[obj.GetName()] = obj
    return objDict

def findMatchingObjects(noAnimChildren, animChildren):
    noAnimDict = getObjectsByName(noAnimChildren)
    animDict   = getObjectsByName(animChildren)

    matchingNoAnim = []
    matchingAnim   = []

    for name, animObj in animDict.items():
        if name in noAnimDict:
            matchingNoAnim.append(noAnimDict[name])
            matchingAnim.append(animObj)

    return matchingNoAnim, matchingAnim

def copy(noAnimObj, animObj):
    noAnimChildren = getAllChildren(noAnimObj)
    animChildren = getAllChildren(animObj)
    matchingNoAnim, matchingAnim = findMatchingObjects(noAnimChildren, animChildren)

    index = 0
    for noAni, ani in zip(matchingNoAnim, matchingAnim):
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, noAni)
        i = copyAni(noAni, ani)
        index += i

    return index


class CopyAniUI(c4d.gui.GeDialog):
    TEXTID       = 416123
    TEXTID2      = 319036
    TEXTID3      = 3992723
    MAINLAYOUTID = 10086
    BUTTONID     = 1008611
    TARGETID     = 15180
    SOURCEID     = 39927

    UI_INSTANCE = None
    @classmethod
    def UIDisplay(cls):
        if cls.UI_INSTANCE is None:
            cls.UI_INSTANCE = CopyAniUI()
        else:
            cls.UI_INSTANCE.Open(dlgtype=c4d.DLG_TYPE_ASYNC)

    def __init__(self, *args, **kwargs):
        super(CopyAniUI, self).__init__(*args, **kwargs)
        self.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=0,
                  xpos=-2, ypos=-2, defaultw=250, defaulth=100, subid=0)

    def CreateLayout(self):
        self.SetTitle('Copy Keys')
        self.layout1()
        self.GroupEnd()
        return True

    # ---------------------------------------------------------
    def layout1(self):
        self.GroupBegin(self.MAINLAYOUTID, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, cols=2, rows=1, title="",
                        groupflags=c4d.BFV_GRIDGROUP_EQUALCOLS, initw=0, inith=0)

        self.AddStaticText(self.TEXTID, flags=c4d.BFH_RIGHT, name=' Target:')
        self.AddCustomGui(self.TARGETID, c4d.CUSTOMGUI_LINKBOX, 'Link Object', c4d.BFH_SCALEFIT, 100, 0)
        self.AddStaticText(self.TEXTID2, flags=c4d.BFH_RIGHT, name=' Source:')
        self.AddCustomGui(self.SOURCEID, c4d.CUSTOMGUI_LINKBOX, 'Link Object2', c4d.BFH_SCALEFIT, 100, 0)
        self.AddStaticText(self.TEXTID3, flags=c4d.BFH_RIGHT, name='')
        self.AddButton(self.BUTTONID, flags=c4d.BFH_RIGHT, initw=100 ,inith=20 ,name='Copy!')

    def Command(self, _id, message):
        if _id == self.BUTTONID:
            noAnimObj = self.FindCustomGui(self.TARGETID, c4d.CUSTOMGUI_LINKBOX).GetData()
            animObj = self.FindCustomGui(self.SOURCEID, c4d.CUSTOMGUI_LINKBOX).GetData()
            if noAnimObj is None or animObj is None:
                c4d.gui.MessageDialog('Please add target and source !')
                raise RuntimeError('Please add target or source !')

            doc.StartUndo()
            index = copy(noAnimObj, animObj)
            c4d.gui.MessageDialog('Replaced animation for {} objects!'.format(index))
            doc.EndUndo()
            c4d.EventAdd()
        return True

if __name__ == '__main__':
    CopyAniUI.UIDisplay()

'''
Revision History
Revision 1: 2024-07-26 : First publish

code by kangddan
https://github.com/kangddan
https://animator.at8.fun/
https://space.bilibili.com/174575687
https://x.com/kangddan1
'''