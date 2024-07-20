import c4d
#Welcome to the world of Python


def main():
    bd = doc.GetActiveBaseDraw()
    if bd[c4d.BASEDRAW_DISPLAYFILTER_SPLINE] == True:
        bd[c4d.BASEDRAW_DISPLAYFILTER_SPLINE] = False
        bd[c4d.BASEDRAW_DISPLAYFILTER_JOINT] = False

        bd[c4d.BASEDRAW_DISPLAYFILTER_MULTIAXIS] = True
        bd[c4d.BASEDRAW_DISPLAYFILTER_NULL] = False
        bd[c4d.BASEDRAW_DISPLAYFILTER_WORLDAXIS] = False
    else:
        bd[c4d.BASEDRAW_DISPLAYFILTER_SPLINE] = True
        bd[c4d.BASEDRAW_DISPLAYFILTER_JOINT] = True

        bd[c4d.BASEDRAW_DISPLAYFILTER_MULTIAXIS] = True
        bd[c4d.BASEDRAW_DISPLAYFILTER_NULL] = True
        bd[c4d.BASEDRAW_DISPLAYFILTER_WORLDAXIS] = True
    bd.Message(c4d.MSG_CHANGE)
    c4d.EventAdd()
if __name__=='__main__':
    main()