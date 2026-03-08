-- threaded customization script: FollowPathThreaded.lua

sim = require('sim')
simIK = require('simIK')
simOMPL = require('simOMPL')
---------------------------------
-- GLOBAL PARAMS
---------------------------------
params = {}

params.maxVelDeg = 90
params.maxAccelDeg = 40

params.omplMaxTime = 5
params.simplifyTime = 5
params.interpolatePts = 200

params.validationStep = 5
params.goalThreshold = 0.02
params.maxExecutionTime = 120

params.objects ={'/Floor','/MPO_700','/assembly_table','/obs1','/obs2','/obs0','/column0','/column1','/column2'}
for i=1,#params.objects do
    local h = sim.getObject(params.objects[i])
    print(params.objects[i], h)
end
-- Robot joints
params.joints = {}
for i = 1, 6 do
    params.joints[i] = sim.getObject('/UR10/joint'..i)
end

---------------------------------
---Initialise Robot parameters
---------------------------------
function initRobot()

    params.joints = {}
    for i=1,6 do
        params.joints[i] = sim.getObject('/UR10/joint'..i)
    end

    params.tip = sim.getObject('/UR10/tip')
    params.base = sim.getObject('/UR10')
    params.target = sim.getObject('/UR10/target')

    params.robotCollection = sim.createCollection()
    sim.addItemToCollection(
        params.robotCollection,
        sim.handle_tree,
        params.base,
        0
    )

    params.gripperCollection = sim.createCollection()
    sim.addItemToCollection(
        params.gripperCollection,
        sim.handle_tree,
        sim.getObject('/UR10/RG2'),
        0
    )

    local vel = params.maxVelDeg * math.pi/180
    local acc = params.maxAccelDeg * math.pi/180

    params.minMaxVel = {}
    params.minMaxAccel = {}

    for i=1,6 do
        params.minMaxVel[#params.minMaxVel+1] = -vel
        params.minMaxVel[#params.minMaxVel+1] = vel

        params.minMaxAccel[#params.minMaxAccel+1] = -acc
        params.minMaxAccel[#params.minMaxAccel+1] = acc
    end

end

pathDrawing = sim.addDrawingObject(
        sim.drawing_linestrip,
        2,              -- line width
        0,
        -1,
        10000,
        {0,0,1}         -- red
    )


-- FK limits (example)
local fkVel, fkAccel, fkJerk = 180, 40, 80
params.fkMaxVel = {fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180}
params.fkMaxAccel = {fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180}

-- Signal to receive path from Python
local pathSignalName = 'FollowPathSignal'
local timeSignalName = 'FollowPathTimes'
local moveToPoseSignalName ='moveToPose'
--------------------------------
---Util funcitons
--------------------------------
function extractConfig(path, index)
    local n = #params.joints
    local c = {}
    local offset = (index-1)*n
    for i=1,n do
        c[i] = path[offset+i]
    end
    return c
end
function getConfig()
    local c = {}
    for i=1,#params.joints do
        c[i] = sim.getJointPosition(params.joints[i])
    end
    return c
end
function getCurrentConfig()
    local config = {}

    for i=1,#params.joints do
        config[i] = sim.getJointPosition(params.joints[i])
    end

    return config
end
function setConfig(config)
    for i=1,#params.joints do
        sim.setJointPosition(params.joints[i], config[i])
    end
end
function l2norm(a,b)
    local s=0
    for i=1,#a do
        local d=a[i]-b[i]
        s=s+d*d
    end
    return math.sqrt(s)
end
function l2_norm_diff(a, b)
    local s = 0.0
    for i = 1, #a do
        local d = a[i] - b[i]
        s = s + d*d
    end
    return math.sqrt(s)
end

function isConfigValid(robotCollection, objectCollection)

    local result = sim.checkCollision(robotCollection, objectCollection)

    return result == 0
end

function flattenConfigs(configs)

    local flat = {}

    for i=1,#configs do
        for j=1,#configs[i] do
            table.insert(flat, configs[i][j])
        end
    end

    return flat
end
function configDistance(q1, q2)
    local d = 0
    for i=1,#q1 do
        local diff = q1[i] - q2[i]
        d = d + diff*diff
    end
    return math.sqrt(d)
end
--------------------------------------------------
-- IK SETUP
--------------------------------------------------
function filterConfigDiversity(configs, threshold)

    local filtered = {}

    for i=1,#configs do

        local keep = true

        for j=1,#filtered do
            if configDistance(configs[i], filtered[j]) < threshold then
                keep = false
                break
            end
        end

        if keep then
            table.insert(filtered, configs[i])
        end
    end

    return filtered
end
function limitConfigs(configs, maxCount)

    local result = {}

    for i=1,math.min(maxCount,#configs) do
        table.insert(result, configs[i])
    end

    return result
end
function validateConfig(config, auxData)

    local joints = auxData.joints
    local robotCollection = auxData.robotCollection
    local objectCollection = auxData.objectCollection

    -- apply candidate configuration
    for i=1,#joints do
        sim.setJointPosition(joints[i], config[i])
    end

    -- collision test
    local coll = sim.checkCollision(robotCollection, objectCollection)

    return coll == 0
end
function findConfigs(goalPose, robotCollection, objectCollection)

    -- 1. create IK environment
    local ikEnv = simIK.createEnvironment()

    -- 2. create IK group
    local ikGroup = simIK.createGroup(ikEnv)

    -- 3. add element from scene
    local ikElement, simToIk, ikToSim =
        simIK.addElementFromScene(
            ikEnv,
            ikGroup,
            params.base,
            params.tip,
            params.target,
            simIK.constraint_pose
        )

    -- 4. map simulation joints ? IK joints
    local ikJoints = {}

    for i=1,#params.joints do
        ikJoints[i] = simToIk[params.joints[i]]
    end

    -- 5. set goal pose
    sim.setObjectPose(params.target, -1, goalPose)

    -- 6. sync scene ? IK environment
    simIK.syncFromSim(ikEnv, {ikGroup})

    -- aux data for callback
    local auxData = {
        joints = params.joints,
        robotCollection = robotCollection,
        objectCollection = objectCollection
    }

    -- parameters
    local p = {
        maxDist = 0.5,
        maxTime = 3,
        pMetric = {1,1,1,0.1},
        cMetric = {1,1,1,1,1,1},
        findMultiple = true,
        findAlt = true,
        cb = validateConfig,
        auxData = auxData
    }
    local original = {}

    for i=1,#params.joints do
        original[i] = sim.getJointPosition(params.joints[i])
    end

    
    -- 7. find IK configs
    local configs = simIK.findConfigs(
        ikEnv,
        ikGroup,
        ikJoints,
        p
    )
    -- restore after collision check
    for i=1,#params.joints do
        sim.setJointPosition(params.joints[i], original[i])
    end

    -- 8. destroy IK environment
    simIK.eraseEnvironment(ikEnv)

    return configs
end
--------------------------------------------------
-- COLLISION SETUP
--------------------------------------------------

function createObjectCollection(graspedObject)

    local coll = sim.createCollection()

    for i=1,#params.objects do
        local h = sim.getObject(params.objects[i])

        if h ~= -1 then
            if graspedObject == nil or h ~= graspedObject then
                sim.addItemToCollection(
                    coll,
                    sim.handle_tree,
                    h,
                    0
                )
            end
        else
            print("WARNING: object not found:", params.objects[i])
        end
    end

    return coll
end

function createRobotCollection(graspedObject)
    local robotCollection = sim.createCollection()

    sim.addItemToCollection(
        robotCollection,
        sim.handle_tree,
        params.base,
        0
    )
    if graspedObject then
        sim.addItemToCollection(
            robotCollection,
            sim.handle_tree,
            graspedObject,
            1
        )
    end
    return robotCollection
end
-------------------------------------------------------
---visualise path
-------------------------------------------------------
function visualizePath(path)

    sim.addDrawingObjectItem(pathDrawing, nil)

    local dof = #params.joints
    local originalConfig = {}

    for i=1,dof do
        originalConfig[i] = sim.getJointPosition(params.joints[i])
    end

    for i=1,#path/dof do

        local config = {}

        for j=1,dof do
            config[j] = path[(i-1)*dof + j]
            sim.setJointPosition(params.joints[j], config[j])
        end

        local pos = sim.getObjectPosition(params.tip, -1)
        sim.addDrawingObjectItem(pathDrawing, pos)

    end

    -- restore robot state
    for i=1,dof do
        sim.setJointPosition(params.joints[i], originalConfig[i])
    end
end
-------------------------------------
-- OMPL PLANNING
--------------------------------------------------

function planPath(goalConfig, graspedObject)

    sim.setStringSignal('MotionStatus', 'planning')
    print('Planning ...')

    local task = simOMPL.createTask('task')

    local useForProjection = {1,1,1,0,0,0}

    simOMPL.setStateSpaceForJoints(
        task,
        params.joints,
        useForProjection
    )

    local objectCollection = createObjectCollection(graspedObject)
    local robotCollection = createRobotCollection(graspedObject)
    params.robotCollection = robotCollection
    local collisionPairs = {
        robotCollection,
        objectCollection,
        robotCollection,
        robotCollection
    }

    simOMPL.setCollisionPairs(task, collisionPairs)
    print('Collision pairs set')

    local startConfig = getConfig()

    simOMPL.setStartState(task, startConfig)




    simOMPL.setGoalStates(task, goalConfig)
    print('goal state set')
    simOMPL.setAlgorithm(task,simOMPL.Algorithm.RRTConnect)
    simOMPL.setStateValidityCheckingResolution(task, 0.002)
    simOMPL.setup(task)
    print('task setup complete')
    local success = simOMPL.solve(task, params.omplMaxTime)
    print('solving task...')
    if not success or not simOMPL.hasExactSolution(task) then
        simOMPL.destroyTask(task)
        sim.destroyCollection(objectCollection)
        sim.setStringSignal('MotionResult', 'no_path')
        sim.setStringSignal('MotionStatus', 'failed')
        return nil
    end

    simOMPL.simplifyPath(task, params.simplifyTime)

    simOMPL.interpolatePath(task, params.interpolatePts)

    local path = simOMPL.getPath(task)

    print("OMPL states:", #path/#params.joints)

    simOMPL.destroyTask(task)
    sim.destroyCollection(objectCollection)

    return path
end

--------------------------------
---Path validation
--------------------------------

function validatePath(path,graspedObject)

    print("Validating path...")
    if #path <2 then
        return false
    end
    local states = #path/#params.joints
    local objectCollection = createObjectCollection(graspedObject)
    local robotCollection = createRobotCollection(graspedObject)

    for i=1,states,params.validationStep do

        local config = extractConfig(path, i)

        setConfig(config)

        local coll,collidingObjects = sim.checkCollision(
            robotCollection,
            objectCollection
        )

        if coll > 0 then
            print("Collision detected at state:", i)
            print("Collision pairs:",sim.getObjectAlias(collidingObjects[1]),sim.getObjectAlias(collidingObjects[2]))
            return false
        end

    end

    return true
end

---------------------------------
---Execute Path
---------------------------------
function executePath(pathPts,times)
    -- Convert strings back to tables
    print("Excecuting Trajectory")
    local st = sim.getSimulationTime()
    local dt = 0

    while dt < times[#times] do
        local config = sim.getPathInterpolatedConfig(pathPts, times, dt)
        for i = 1, #params.joints do
            sim.setJointTargetPosition(params.joints[i], config[i])
        end
        sim.wait(sim.getSimulationTimeStep()) -- advance simulation properly
        dt = sim.getSimulationTime() - st
    end
    local finalConfig = sim.getPathInterpolatedConfig(pathPts, times, times[#times])
    local threshold =0.01
    local curr_err = l2_norm_diff(getConfig(params.joints),finalConfig)
    print("current error: ",curr_err)
    while curr_err > threshold do
        -- Finish at last config
        
        for i = 1, #params.joints do
            sim.setJointTargetPosition(params.joints[i], finalConfig[i])
        end
        curr_err = l2_norm_diff(getConfig(params.joints),finalConfig)
        print("current error: ",curr_err)
        sim.wait(0.1)
    end
    sim.wait(0.1)

    -- Clear signals to mark done
    sim.clearStringSignal(pathSignalName) 
    sim.clearStringSignal(timeSignalName)
    sim.setStringSignal('FollowPathDone', '1')
end
function executeTrajectory(pathPts, times)

    sim.setStringSignal('MotionStatus', 'executing')

    local startTime = sim.getSimulationTime()

    local duration = times[#times]

    while true do

        local t = sim.getSimulationTime() - startTime

        if t > duration then
            break
        end

        local config = sim.getPathInterpolatedConfig(
            pathPts,
            times,
            t
        )

        for i=1,#params.joints do
            sim.setJointTargetPosition(
                params.joints[i],
                config[i]
            )
        end
        if sim.getSimulationTime() - startTime > params.maxExecutionTime then
            sim.setStringSignal('MotionResult', 'timeout')
            sim.setStringSignal('MotionStatus', 'failed')
            return false
        end

        sim.wait(sim.getSimulationTimeStep())

    end

    local goal = extractConfig(
        pathPts,
        #pathPts/#params.joints
    )

    local curr_err = l2_norm_diff(getConfig(params.joints),goal)
    print("current error: ",curr_err)
    while curr_err > params.goalThreshold do
        -- Finish at last config
        curr_err = l2_norm_diff(getConfig(params.joints),goal)
        print("current error: ",curr_err)
        sim.wait(0.1)
    end
    local err = l2norm(getConfig(), goal)
    print("Final error:", err)

    if err > params.goalThreshold then
        sim.setStringSignal('MotionResult', 'timeout')
        sim.setStringSignal('MotionStatus', 'failed')
        return false
    end

    sim.setStringSignal('MotionResult', 'success')
    sim.setStringSignal('MotionStatus', 'done')
    sim.setStringSignal('ExecutionTime',sim.getSimulationTime()-startTime)

    return true
end

--------------------------------
---Generate Trajectroy
--------------------------------
function generateTrajectory(path)
    local lengths =sim.getPathLengths(
        path,
        #params.joints
    )
    local pathPts, times = sim.generateTimeOptimalTrajectory(
        path,
        lengths,
        params.minMaxVel,
        params.minMaxAccel,
        1000,
        'not-a-knot',
        5,
        nil
    )
    
    print("Trajectory points:", #pathPts/#params.joints)
    print("Duration:",times[#times])

    return pathPts,times
end

--------------------------------
---Main Loop
--------------------------------
function sysCall_thread()
    
    initRobot()


    while true do
        -- Check if a new goal config has been sent from python
        -- local goalSignal = sim.getStringSignal('GoalConfig')
        local targetPoseSignal = sim.getStringSignal('TargetPose')

        if targetPoseSignal then
            print('Target signal recieved..')
            -- sim.clearStringSignal('GoalConfig')
            sim.clearStringSignal('TargetPose')
            sim.clearStringSignal('ExecutionTime')
            local graspedObjectName = sim.getStringSignal('GraspedObject')
            local graspedObject = nil
            if graspedObjectName then
                graspedObject = sim.getObject(graspedObjectName)
            end
            robotCollection = createRobotCollection(graspedObject)
            objectCollection = createObjectCollection(graspedObject)
            local goalPose = sim.unpackTable(targetPoseSignal)
            --local goalConfig = sim.unpackTable(goalSignal)
            local configs = findConfigs(goalPose,robotCollection,objectCollection)
            local goalConfigs = filterConfigDiversity(configs,0.2)
            --local goalConfigs = goalPose

            print("IK solutions found:", #goalConfigs)
            if #goalConfigs == 0 then
                print("No valid IK solutions")
                sim.setStringSignal('MotionResult','no_ik_solution')
                sim.setStringSignal('MotionStatus','failed')
                
           
            else

                local path = planPath(
                    goalConfigs,
                    graspedObject
                )

                --local timeData = sim.getStringSignal(timeSignalName)
                if path then
                    print('path found')
                    visualizePath(path)
                    if validatePath(path,graspedObject)then
                        print('valid path found, generating trajectory...')
                        local pathPts,times = generateTrajectory(path)
                        -- executePath(pathPts,times)
                        print('excecuting path...')
                        executeTrajectory(pathPts,times)
                    else
                        print('path invalid')
                        sim.setStringSignal('MotionResult','collision')
                        sim.setStringSignal('MotionStatus','failed')
                    end
                end
            end
        end
        sim.switchThread() -- yield to let sim continue
    end
end





