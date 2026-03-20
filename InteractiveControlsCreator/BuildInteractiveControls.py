from maya import cmds


def get_hierarchy(pObj, pType: str = "transform"):
    return cmds.listRelatives(pObj, children=True, allDescendents=True, fullPath=True, type=pType) + [pObj]


def build_interactive_controls():
    """
    It builds an interactive setup with locators and controls where the user can update the position of the joints without updating the skin manually

    Steps :
    1. store the selection
    2. store the hierarchy
    3. create a list from selection and hierarchy
    4. store the skins
    5. For all bone, create locators
    6. For selected bones, create controllers
    7. Connect each locator to the bind Pre matrix of each skin
    @return:
    """
    # TODO : when adding a new controller to an existing setup, it should be good that the new setup is parented and parenting the the existing.

    # get all selected
    sel = cmds.ls(sl=1, l=True)

    # get all children and add them to sel, but pre-store all children to avoid creation of controllers
    hierarchyList = []
    for bone in sel:
        children = get_hierarchy(bone)
        for b in children:
            if b not in hierarchyList:
                hierarchyList.append(b)

    mergedList = sel.copy()
    for h in hierarchyList:
        if h not in mergedList:
            mergedList.append(h)

    boneList = sorted(mergedList, key=lambda t: (t.count('|'), len(t)))
    print(boneList)
    # get all skins from all bones
    skinList = []
    for bone in boneList:
        skin = cmds.ls(cmds.listHistory(bone, future=True), type='skinCluster')
        if not skin:
            continue
        for s in skin:
            if s not in skinList:
                skinList.append(s)

    # setup
    for bone in boneList:
        boneName = bone.split("|")[-1]
        # locators :
        loc = cmds.spaceLocator(n="loc_" + boneName)
        cmds.addAttr(loc[0], longName='isInteractiveSetup', attributeType='bool', defaultValue=True, keyable=False)
        boneParent = cmds.listRelatives(bone, parent=True, type="transform", fullPath=False)
        locParent = "loc_" + boneParent[0] if boneParent else None
        print(loc, locParent)
        if locParent and cmds.ls(locParent):
            cmds.parent(loc, locParent)
        cmds.matchTransform(loc, bone)

        # only create full setup for selected
        if bone in sel:
            # controllers :
            ctrl = cmds.circle(n="ctrl_" + boneName, normal=[1, 0, 0], c=(0, 0, 0))
            cmds.addAttr(ctrl[0], longName='isInteractiveSetup', attributeType='bool', defaultValue=True,
                         keyable=False)
            ctrlParent = "ctrl_" + boneParent[0] if boneParent else None
            if ctrlParent and cmds.ls(ctrlParent):
                cmds.parent(ctrl, ctrlParent)

            cmds.connectAttr(loc[0] + ".matrix", ctrl[0] + ".offsetParentMatrix")

            cmds.move(0, 0, 0, ctrl, objectSpace=True)
            cmds.rotate(0, 0, 0, ctrl, objectSpace=True)
            cmds.scale(1, 1, 1, ctrl, objectSpace=True)

            parentConst = cmds.parentConstraint(ctrl, bone)
            cmds.addAttr(parentConst[0], longName='isInteractiveSetup', attributeType='bool', defaultValue=True,
                         keyable=False)
        if skinList:
            # for skin in skinList:
            outBoneConnectionList = cmds.connectionInfo(bone + ".worldMatrix[0]", destinationFromSource=True)
            if outBoneConnectionList:  # that means the bone skin the geo
                for outBoneConnection in outBoneConnectionList:
                    skin, data = outBoneConnection.split(".")
                    index = data.split("[")[-1].split("]")[0]  # retrieve "19" from ['skinCluster11.matrix[19]']
                    cmds.connectAttr(loc[0] + ".worldInverseMatrix[0]", skin + f".bindPreMatrix[{index}]")

build_interactive_controls()
