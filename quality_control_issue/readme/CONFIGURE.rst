To configure this module in order to take advantage of the kanban views you
need to create the stages for *issues* and *problems*. To **create** stages in
any kanban view click on *Add New Column*. Then you can **reorder** the stages
just dragging them.

In created stages you can **configure** them clicking on the gear button that
appears at the right of the stage name and clicking on *Edit*. Note the
following behaviors:

* You can set a *Quality Control Team*.

  - Stages with no team set will be shared by all teams.
  - Stages with a team associated will be only available for that specific
    team.

* In Issue Stages you can also relate a *QC State* to the stage.

  - When you move to a different stage an issue with *QC state* defined the
    state of the issue will also change according to it.
  - The other way around, if you change the state, the system will look for
    an appropriate stage and if existing the issue will be move to that stage.
  - If you change the *QC team* of an issue, the system will get the default
    stage for that team and apply it to the issue.
