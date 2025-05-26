(define (problem stack-by-type)
  (:domain simple-pick-place)

  (:objects
    robot0 - robot
    cube1 cube2 - object
    column1 column2 - object
    regionA1 regionA2 - region
    regionB1 regionB2 - region
    q0 - config ; initial config
  )

  (:init
    ;; Robot starts at q0
    (AtConfig q0)

    ;; Object types (implicitly defined by what we allow them to be placed on)
    (Graspable cube1)
    (Graspable cube2)
    (Graspable column1)
    (Graspable column2)

    ;; Stackable definitions – where each object is allowed to go
    (Stackable cube1 regionA1)
    (Stackable cube1 regionA2)
    (Stackable cube2 regionA1)
    (Stackable cube2 regionA2)
    (Stackable column1 regionB1)
    (Stackable column1 regionB2)
    (Stackable column2 regionB1)
    (Stackable column2 regionB2)

    ;; Start on the table (positions are unknown – Pose will be sampled)
    ;; (Pose cube1 p1) – Not needed. The `stream` will sample pose and grasp.

    ;; The table is assumed clear for stacking, and collisions will be checked by streams
  )

  (:goal
    (and
      (forall (?o - object)
        (or
          ;; If it’s a cube, it must be on a region of type A
          (and (or (= ?o cube1) (= ?o cube2))
               (exists (?r - region) (and (or (= ?r regionA1) (= ?r regionA2))
                                          (exists (?p - pose)
                                            (and (Pose ?o ?p)
                                                 (Supported ?o ?p ?r))))))
          ;; If it’s a column, it must be on a region of type B
          (and (or (= ?o column1) (= ?o column2))
               (exists (?r - region) (and (or (= ?r regionB1) (= ?r regionB2))
                                          (exists (?p - pose)
                                            (and (Pose ?o ?p)
                                                 (Supported ?o ?p ?r))))))
        )
      )
    )
  )
)
