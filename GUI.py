# -*- coding:utf-8 -*-  
import sys
from PyQt4 import QtGui,QtCore
import experiment

class Node(QtGui.QGraphicsEllipseItem):
           def __init__(self,name):
                   super(Node, self).__init__()
                   self.__name = name
                   
           def getName(self):
                      return self.__name
           def changeBrush(self, color, style):
                      b = QtGui.QBrush()
                      b.setStyle(style)
                      c = b.color()
                      c.setRgb(color[0],color[1],color[2])
                      b.setColor(c)
                      self.setBrush(b)

class Link(QtGui.QGraphicsLineItem):
           def __init__(self,name,link_type):
                      super(Link, self).__init__()
                      self.__link_type = link_type
                      self.__name = name
           def getName(self):
                      return self.__name
           def getType(self):
                      return self.__link_type
           def changeType(self,link_type):
                      self.__link_type = link_type
           def changeColor(self,color):
                      p = QtGui.QPen()
                      c = p.color()
                      c.setRgb(color[0],color[1],color[2])
                      p.setColor(c)
                      self.setPen(p)
           
class GUI(QtGui.QWidget):

           def __init__(self):
                      super(GUI, self).__init__()
                      self.exp = experiment.Experiments(20,3)
                      self.matching = self.exp.unidirectional_match()
                      self.initUI()

           def initUI(self):
                      self.setWindowTitle(' Stable Matching ')
                      grid = QtGui.QGridLayout()
                      step_button = QtGui.QPushButton('STEP',self)
                      epoch_button = QtGui.QPushButton('EPOCH',self)
                      end_button = QtGui.QPushButton('END',self)
                      self.showText = QtGui.QTextEdit(self)
                      self.showText.setText('START! ')

                      self.statu_scene = QtGui.QGraphicsScene(self)
                      self.initScene(self.statu_scene)
                      self.statu_view = QtGui.QGraphicsView()
                      self.statu_view.setScene(self.statu_scene) 
                      self.statu_view.setMinimumSize(600,600)
                      self.statu_view.show()

                      self.history_scene = QtGui.QGraphicsScene(self)
                      self.initScene(self.history_scene)
                      self.history_view = QtGui.QGraphicsView()
                      self.history_view.setScene(self.history_scene)
                      self.history_view.setMinimumSize(600,600)
                      self.history_view.show()
                      
                      grid.addWidget(step_button,1,1)
                      grid.addWidget(epoch_button,2,1)
                      grid.addWidget(end_button,3,1)
                      grid.addWidget(self.showText,1,2,5,1)
                      grid.addWidget(self.statu_view,1,3,5,1)
                      grid.addWidget(self.history_view,1,4,5,1)
                      self.setLayout(grid)
                      
                      self.connect(step_button,QtCore.SIGNAL('clicked()'),self.nextStep)
                      self.connect(epoch_button,QtCore.SIGNAL('clicked()'),self.nextEpoch)
                      self.connect(end_button,QtCore.SIGNAL('clicked()'),self.exeToEnd)
                      self.resize(1500,800)
                      
           def initScene(self,scene):
                      man_num = self.exp.get_man_num()
                      woman_num = self.exp.get_woman_num()
                      length = max(man_num,woman_num) * 30
                      scene.setSceneRect(0,0,600,length)

                      for i in range(man_num):
                                 self.__addNode(scene, 'M_'+str(i),120,i*30+10,10,10,(0,0,255))
                      for i in range(woman_num):
                                 self.__addNode(scene, 'W_'+str(i),480,i*30+10,10,10,(255,0,0))

           def __addNode(self, scene, name, x, y, w, h, color=(0,0,0)):
                      node = Node(name)
                      node.setRect(x,y,w,h)
                      node.changeBrush(color,1)
                      scene.addItem(node)

           def __addLink(self, scene, name, node1, node2, color = (0,0,0), link_type = ''):
                      center1 = node1.boundingRect().center()
                      center2 = node2.boundingRect().center()
                      name1 = node1.getName().split('_')[1]
                      name2 = node2.getName().split('_')[1]
                      link = Link(name1 + '-' + name2, link_type)
                      link.setLine(center1.x(),center1.y(),center2.x(),center2.y())
                      link.changeColor(color)
                      scene.addItem(link)

           def __deleteLink(self, scene, name):
                      link = self.__findLink(name, scene.items())
                      scene.removeItem(link)
                      
           def __findNode(self, name, items):
                      for item in items:
                                 if isinstance(item,Node) and name == item.getName():
                                            return item
                      return False

           def __findLink(self,name,items):
                      for item in items:
                                 if isinstance(item,Link) and name == item.getName():
                                            return item
                      return False

           def __clearLinks(self, scene):
                      for item in scene.items():
                                 if isinstance(item,Link) and item.getType() != 'marry':
                                            scene.removeItem(item)

           def __clearUpLinks(self, scene):
                      for item in scene.items():
                                 if isinstance(item, Link):
                                            scene.removeItem(item)

           def __refreshViewStep(self, info):
                      record = info.split('\n')
                      length = len(record)
                      lineiter = 0
                      epoch = record[lineiter].strip().split(':')[1]
                      lineiter += 1
                      step = record[lineiter].strip().split(':')[1]
                      lineiter += 1
                      statu = record[lineiter].strip()
                      if 'DONE' in statu:
                                 return 0
                      elif 'is not activity' in statu:
                                 return 1
                      elif 'is married' in statu:
                                 return 2 
                      couple = statu.replace(' ','').split('target')
                      man = self.__findNode('M_'+couple[0], self.statu_scene.items())
                      woman = self.__findNode('W_'+couple[1], self.statu_scene.items())
                      lineiter += 1
                      sui_rank = record[lineiter].replace(' ','').split(':')[1]
                      lineiter += 1
                      if 'Husband Rank' in record[lineiter]:
                                 husband_rank = record[lineiter].replace(' ','').split(':')[1]
                                 lineiter += 1
                      if 'Succeed' in record[lineiter]:
                                 self.__addLink(self.statu_scene, couple[0] + '-' + couple[1], man, woman, link_type = 'marry')
                                 self.__addLink(self.history_scene, couple[0] + '-' + couple[1], man, woman, link_type = 'marry')
                                 lineiter += 1
                                 if lineiter <= length:
                                            if 'threw away' in record[lineiter]:
                                                       throwCouple = record[lineiter].replace(' ','').split('threwaway')
                                                       link = self.__findLink(throwCouple[1] + '-' + throwCouple[0],self.statu_scene.items())
                                                       link.changeType('break')
                                                       link.changeColor((0,255,0))
                                                       node1 = self.__findNode('M_' + throwCouple[1], self.history_scene.items())
                                                       node2 = self.__findNode('W_' + throwCouple[0], self.history_scene.items())
                                                       self.__addLink(self.history_scene, throwCouple[1] + '-' + throwCouple[0], node1, node2, (0,255,0) , 'break')
                                                       self.__deleteLink(self.statu_scene, throwCouple[1] + '-' + throwCouple[0])
                                 self.statu_view.update()
                                 self.history_view.update()
                      elif 'Failed' in record[lineiter]:
                                 #self.__addLink(self.statu_scene, couple[0] + '-' + couple[1], man, woman, (0,0,255) , 'failed')
                                 self.__addLink(self.history_scene, couple[0] + '-' + couple[1], man, woman, (0,0,255) , 'failed')
                                 self.statu_view.update()
                                 self.history_view.update()
                      
           def nextStep(self):
                      info = self.matching.step()
                      self.showText.setText(info)
                      self.__clearLinks(self.statu_scene)
                      self.__clearUpLinks(self.history_scene)
                      self.__refreshViewStep(info)                                 

           def nextEpoch(self):
                      info = self.matching.epoch()
                      self.__clearLinks(self.statu_scene)
                      self.__clearUpLinks(self.history_scene)
                      sep = info.split('\n')[0]
                      records = info.split(sep+'\n')
                      del records[0]
                      for record in records:
                                 self.__refreshViewStep(sep+'\n'+record) 
                      self.showText.setText(info)

           def exeToEnd(self):
                      info = self.matching.exe_to_end()
                      self.__clearLinks(self.statu_scene)
                      self.__clearUpLinks(self.history_scene)
                      records = info.split('EPOCH')
                      del records[0]
                      for record in records:
                                 self.__refreshViewStep('EPOCH'+record)
                      
                      self.showText.setText(info)
           
           def closeEvent(self, event):
                      reply = QtGui.QMessageBox.question(self, 'Message',
                                                         'Are you sure to quit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                      if reply == QtGui.QMessageBox.Yes:
                                 event.accept()
                      else:
                                 event.ignore()

if __name__ == '__main__':
           app = QtGui.QApplication(sys.argv)
           gui = GUI()
           gui.show()
           sys.exit(app.exec_())
