function setGripperCollision(enable)
    local robotLeftFinger  = sim.getObject('/UR10/ROBOTIQ85/LfingerTipVisible')
    local robotRightFinger = sim.getObject('/UR10/ROBOTIQ85/RfingerTipVisible')
    if enable then
        sim.setBoolProperty(robotLeftFinger, 'collidable', true)
        sim.setBoolProperty(robotRightFinger, 'collidable', true)
    else
        sim.setBoolProperty(robotLeftFinger, 'collidable', false)
        sim.setBoolProperty(robotRightFinger, 'collidable', false)
    end
end
-- Helper: get current joint positions
function getConfig(joints)
    local c = {}
    for i=1,#joints do
        c[i] = sim.getJointPosition(joints[i])
    end
    return c
end

-- Helper: set joint positions
function setConfig(config, joints)
    for i=1,#joints do
        sim.setJointPosition(joints[i], config[i])
    end
end


-- Helper: simple collision check for a list of configs
function collides(configs, robotCollection, joints)
    local bufferedConfig = getConfig(joints)
    for i=1,#configs do
        setConfig(configs[i], joints)
        local res = sim.checkCollision(robotCollection, sim.handle_all)
        if res > 0 then
            setConfig(bufferedConfig, joints)
            return true
        else
            res = sim.checkCollision(robotCollection, robotCollection)
            if res > 0 then
                setConfig(bufferedConfig, joints)
                return true
            end
        end
    end
    setConfig(bufferedConfig, joints)
    return false
end

-- Helper: compute an IK path
function computeIKPath(robotBase, robotTip, robotTarget, joints)
    local ikEnv = simIK.createEnvironment()
    local ikGroup = simIK.createGroup(ikEnv)
    local ikEl, simToIk, ikToSim = simIK.addElementFromScene(ikEnv, ikGroup, robotBase, robotTip, robotTarget, simIK.constraint_pose)
    local ikJoints = {}
    for i=1,#joints do
        ikJoints[i] = simToIk[joints[i]]
    end
    local path = simIK.generatePath(ikEnv, ikGroup, ikJoints, simToIk[robotTip], 4)
    simIK.eraseEnvironment(ikEnv)
    if path then
        -- reshape into NxM table
        local nJ = #joints
        local reshaped = {}
        for i=1,#path/nJ do
            local row = {}
            for j=1,nJ do
                row[j] = path[(i-1)*nJ+j]
            end
            table.insert(reshaped, row)
        end
        path = reshaped
    end
    return path
end

-- Helper: build passive visualization shape
function buildPassiveVizShape(robotBase)
    local objectList = sim.getObjectsInTree(robotBase, sim.sceneobject_shape)
    local filtered = {}
    for i=1,#objectList do
        if sim.getBoolProperty(objectList[i], sim.boolprop_visible) then
            table.insert(filtered, objectList[i])
        end
    end
    filtered = sim.copyPasteObjects(filtered)
    local passiveVizShape = sim.groupShapes(filtered, true)
    local props = {'respondable','dynamic','collidable','measurable','detectable'}
    for i=1,#props do
        sim.setBoolProperty(passiveVizShape, props[i], false)
    end
    local meshHandles = sim.getIntArrayProperty(passiveVizShape, sim.intparam_mesh_triangles)
    if meshHandles and #meshHandles>0 then
        sim.setColorProperty(meshHandles[1], sim.colorcomponent_diffuse, {1,0,0})
    end
    sim.setObjectAlias(passiveVizShape, 'passiveVisualizationShape')
    return passiveVizShape
end

-- Main function: select one valid config
function selectOneValidConfig(configs, approachIKTr, withdrawIkTr, robotCollection, joints, robotBase, robotTip, robotTarget, gripper)
    local retVal = nil
    local passiveVizShape = nil
    local bufferedConfig = getConfig(joints)

    local i = 1
    while i <= #configs do
        local target = configs[i]

        -- Base collision check
        if collides({target}, robotCollection, joints) then
            table.remove(configs, i)
        else
            setConfig(target, joints)

            -- Disable gripper collision
            setGripperCollision( false)

            -- Approach check
            if approachIKTr then
                local pose = sim.getObjectPose(robotTip)
                local targetPose = sim.multiplyPoses(pose, approachIKTr)
                sim.setObjectPose(robotTarget, targetPose)
                local path = computeIKPath(robotBase, robotTip, robotTarget, joints)
                if not path or collides(path, robotCollection, joints) then
                    table.remove(configs, i)
                    setGripperCollision( true)
                    goto continue_loop
                end
            end

            -- Withdraw check
            if withdrawIkTr then
                targetPose = sim.multiplyPoses(targetPose, withdrawIkTr)
                sim.setObjectPose(robotTarget, targetPose)
                local path = computeIKPath(robotBase, robotTip, robotTarget, joints)
                if not path or collides(path, robotCollection, joints) then
                    table.remove(configs, i)
                    setGripperCollision( true)
                    goto continue_loop
                end
            end

            -- Re-enable gripper collision
            setGripperCollision( true)

            -- Valid config found
            retVal = target
            passiveVizShape = buildPassiveVizShape(robotBase)
            configs = {table.unpack(configs, i)}
            break
        end

        ::continue_loop::
        i = i + 1
    end

    setConfig(bufferedConfig, joints)
    return retVal, passiveVizShape, configs
end
