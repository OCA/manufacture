 * Go to Manufacturing > Configuration > Work Centers
 * Set parent field on workcenters

 * Go to Manufacturing > Configuration > Settings
 * Set the parent level empty configuration if needed.

 Without setting this parameter, the parent levels are always set, never mind the depth
 of the parent workcenters. The last parent level will contain the last parent and 
 the top parent workcenter, will appear it self in its parent level.
 The idea is to be able to see group of workcenters : 

  ../static/src/img/img1.png

 With the parameter, the parent levels will be empty if the depth of the parent is
 to small. (ie : a workcenter with 1 parent and 1 great parent will have parent level 1 and 2 set, but parent level 3 will be empty)

  ../static/src/img/img2.png
