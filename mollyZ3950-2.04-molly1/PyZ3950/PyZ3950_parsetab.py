
# PyZ3950_parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftLOGOPATTRSET COMMA LOGOP LPAREN QUAL QUOTEDVALUE RELOP RPAREN SET SLASH WORDtop : cclfind_or_attrsetcclfind_or_attrset : cclfindcclfind_or_attrset : ATTRSET LPAREN WORD SLASH cclfind RPARENcclfind : cclfind LOGOP elementscclfind : elementselements : LPAREN cclfind RPARENelements : SET RELOP WORDelements : valelements : quallist RELOP valquallist : QUALquallist : quallist COMMA QUALval : QUOTEDVALUEval : val WORDval : WORD'
    
_lr_action_items = {'QUOTEDVALUE':([0,12,14,18,26,],[1,1,1,1,1,]),'LOGOP':([1,3,4,5,6,13,19,20,22,24,25,27,],[-12,-5,-14,-8,14,-13,14,-4,-7,-9,-6,14,]),'SET':([0,12,14,26,],[10,10,10,10,]),'WORD':([0,1,4,5,12,13,14,15,16,18,24,26,],[4,-12,-14,13,4,-13,4,21,22,4,13,4,]),'RELOP':([9,10,11,23,],[-10,16,18,-11,]),'SLASH':([21,],[26,]),'ATTRSET':([0,],[8,]),'QUAL':([0,12,14,17,26,],[9,9,9,23,9,]),'COMMA':([9,11,23,],[-10,17,-11,]),'LPAREN':([0,8,12,14,26,],[12,15,12,12,12,]),'RPAREN':([1,3,4,5,13,19,20,22,24,25,27,],[-12,-5,-14,-8,-13,25,-4,-7,-9,-6,28,]),'$end':([1,2,3,4,5,6,7,13,20,22,24,25,28,],[-12,-1,-5,-14,-8,-2,0,-13,-4,-7,-9,-6,-3,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'cclfind_or_attrset':([0,],[2,]),'elements':([0,12,14,26,],[3,3,20,3,]),'val':([0,12,14,18,26,],[5,5,5,24,5,]),'top':([0,],[7,]),'cclfind':([0,12,26,],[6,19,27,]),'quallist':([0,12,14,26,],[11,11,11,11,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> top","S'",1,None,None,None),
  ('top -> cclfind_or_attrset','top',1,'p_top','ccl.py',170),
  ('cclfind_or_attrset -> cclfind','cclfind_or_attrset',1,'p_cclfind_or_attrset_1','ccl.py',174),
  ('cclfind_or_attrset -> ATTRSET LPAREN WORD SLASH cclfind RPAREN','cclfind_or_attrset',6,'p_cclfind_or_attrset_2','ccl.py',178),
  ('cclfind -> cclfind LOGOP elements','cclfind',3,'p_ccl_find_1','ccl.py',182),
  ('cclfind -> elements','cclfind',1,'p_ccl_find_2','ccl.py',186),
  ('elements -> LPAREN cclfind RPAREN','elements',3,'p_elements_1','ccl.py',190),
  ('elements -> SET RELOP WORD','elements',3,'p_elements_2','ccl.py',212),
  ('elements -> val','elements',1,'p_elements_3','ccl.py',218),
  ('elements -> quallist RELOP val','elements',3,'p_elements_4','ccl.py',222),
  ('quallist -> QUAL','quallist',1,'p_quallist_1','ccl.py',229),
  ('quallist -> quallist COMMA QUAL','quallist',3,'p_quallist_2','ccl.py',233),
  ('val -> QUOTEDVALUE','val',1,'p_val_1','ccl.py',237),
  ('val -> val WORD','val',2,'p_val_2','ccl.py',241),
  ('val -> WORD','val',1,'p_val_3','ccl.py',245),
]
