(define (domain simple-pick-place)
  (:requirements :strips :typing :equality)

  (:types object region pose grasp config traj)

  (:predicates
    ;; Object classifications
    (IsCube ?o - object)
    (IsColumn ?o - object)
    (IsRegionA ?r - region)
    (IsRegionB ?r - region)

    ;; Pose and grasp info
    (Pose ?o - object ?p - pose)
    (Grasp ?o - object ?g - grasp)
    (Kin ?o - object ?p - pose ?g - grasp ?q - config ?t - traj)

    ;; Motion feasibility
    (FreeMotion ?q1 - config ?t - traj ?q2 - config)
    (HoldingMotion ?q1 - config ?t - traj ?q2 - config ?o - object ?g - grasp)
    (Traj ?t - traj)

    ;; Current robot state
    (AtConf ?q - config)
    (HandEmpty)
    (AtPose ?o - object ?p - pose)
    (AtGrasp ?o - object ?g - grasp)
    (CanMove)

    ;; Object placement semantics
    (Supported ?o - object ?p - pose ?r - region)
    (AssignedRegion ?o - object ?r - region)

    ;; Collision checks
    (CFreeTrajPose ?t - traj ?o2 - object ?p2 - pose)
    (CFreeApproachPose ?o - object ?p - pose ?g - grasp ?o2 - object ?p2 - pose)

    ;; Derived: current holding and object on region
    (Holding ?o - object)
    (On ?o - object ?r - region)

    ;; Derived: safety checks
    (UnsafeApproach ?o - object ?p - pose ?g - grasp)
    (UnsafeTraj ?t - traj)
  )

  ;; Actions

  (:action move_free
    :parameters (?q1 ?q2 ?t)
    :precondition (and (FreeMotion ?q1 ?t ?q2)
                       (AtConf ?q1) (HandEmpty) (CanMove))
    :effect (and (AtConf ?q2)
                 (not (AtConf ?q1))
                 (not (CanMove)))
  )

  (:action move_holding
    :parameters (?q1 ?q2 ?o ?g ?t)
    :precondition (and (HoldingMotion ?q1 ?t ?q2 ?o ?g)
                       (AtConf ?q1) (AtGrasp ?o ?g) (CanMove))
    :effect (and (AtConf ?q2)
                 (not (AtConf ?q1))
                 (not (CanMove)))
  )

  (:action pick
    :parameters (?o ?p ?g ?q ?t)
    :precondition (and (Kin ?o ?p ?g ?q ?t)
                       (AtPose ?o ?p) (HandEmpty) (AtConf ?q)
                       (not (UnsafeApproach ?o ?p ?g))
                       (not (UnsafeTraj ?t)))
    :effect (and (AtGrasp ?o ?g) (CanMove)
                 (not (AtPose ?o ?p))
                 (not (HandEmpty)))
  )

  (:action place
    :parameters (?o ?p ?g ?q ?t ?r)
    :precondition (and (Kin ?o ?p ?g ?q ?t)
                       (AtGrasp ?o ?g) (AtConf ?q)
                       (AssignedRegion ?o ?r)
                       (Supported ?o ?p ?r)
                       (not (UnsafeApproach ?o ?p ?g))
                       (not (UnsafeTraj ?t)))
    :effect (and (AtPose ?o ?p) (HandEmpty) (CanMove)
                 (not (AtGrasp ?o ?g)))
  )

  ;; Derived predicates

  (:derived (On ?o ?r)
    (exists (?p) (and (Supported ?o ?p ?r)
                      (AtPose ?o ?p)))
  )

  (:derived (Holding ?o)
    (exists (?g) (and (Grasp ?o ?g)
                      (AtGrasp ?o ?g)))
  )

  (:derived (UnsafeApproach ?o ?p ?g)
    (exists (?o2 ?p2)
      (and (Pose ?o ?p) (Grasp ?o ?g) (Pose ?o2 ?p2)
           (not (= ?o ?o2))
           (not (CFreeApproachPose ?o ?p ?g ?o2 ?p2))
           (AtPose ?o2 ?p2)))
  )

  (:derived (UnsafeTraj ?t)
    (exists (?o2 ?p2)
      (and (Traj ?t) (Pose ?o2 ?p2)
           (not (CFreeTrajPose ?t ?o2 ?p2))
           (AtPose ?o2 ?p2)))
  )
)
