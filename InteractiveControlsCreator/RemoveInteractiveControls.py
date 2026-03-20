from maya import cmds


def remove_interactive_controls():
    for bone in cmds.ls(type="joint"):
        out = cmds.ls(cmds.listHistory(bone, future=True), type="parentConstraint")
        for const in out:
            if cmds.attributeQuery("isInteractiveSetup", node=const, exists=True):
                cmds.delete(const)

    # because we can't only remove the connection, we have to set the matrix right after disconnection to set it.
    # sometimes, disconnecting a connection automatically set the input to 0
    for skin in cmds.ls(type="skinCluster"):
        # below: could also use for inConnection in cmds.getAttr(skin + '.bindPreMatrix', multiIndices=True)
        for inConnection in cmds.ls(skin + ".bindPreMatrix[*]"):
            mat = cmds.getAttr(inConnection)
            inBoneConnection = cmds.connectionInfo(inConnection, sourceFromDestination=True)
            if inBoneConnection:
                cmds.disconnectAttr(inBoneConnection, inConnection)
                cmds.setAttr(inConnection, mat, type="matrix")

    for obj in cmds.ls(type="transform"):
        try:
            if cmds.attributeQuery("isInteractiveSetup", node=obj, exists=True):
                cmds.delete(obj)
        except TypeError:
            # because if we delete top element, children will be deleted too
            pass

    cmds.select(clear=True)
    
remove_interactive_controls()
