import rclpy
from rclpy.node import Node
from simulation.config_planning import RoboticsEnvironment
from std_msgs.msg import String
import networkx as nx
import matplotlib.pyplot as plt



class Observer(Node):
    '''
    A publisher node publishing a scenegraph all the time
    '''
    def __init__(self):
        super().__init__('Observer_node')
        self.publisher_ = self.create_publisher(String,'observation',10)
        self.time_period = 2
        self.timer = self.create_timer(self.time_period,self.timer_callback)
        
        #coppelia env setup
        self.env = RoboticsEnvironment()
        self.env.connect()
        self.env.initialize_params()

        #scene Graph initialisation
        self.scene_graph = nx.Graph()

        self.handleList = ['/column0',
                          '/column1',
                          '/column2',
                          '/column3',
                          '/pillar1',
                          '/pillar2',
                          '/pillar3',
                          '/Cuboid0',
                          '/Cuboid1',
                          '/table1',
                          '/assembly_table'
                          ]
        self.objectList = [self.env.getObject(handle) for handle in self.handleList]
        self.tables =self.objectList[-2:]
        self.objectDict=dict(zip(self.objectList,self.handleList))
        #add all objects to scene graph
        for handle in self.handleList:
            self.scene_graph.add_node(handle)

        fig,ax = plt.subplots()
        self.ax = ax
    def isOn(self,obj1,obj2):
        if self.env.checkCollision(obj1,obj2) :#and not self.env.checkCollision(obj1,obj2,self.tables[0],self.tables[1]):

            return True
        else:
            return False
    def define_relations(self):
        checkList  = self.objectList
        for obj1 in checkList:
            checkList.pop(0)
            for obj2 in checkList:
                if self.isOn(obj1=obj1,obj2=obj2):
                    self.scene_graph.add_edge(self.objectDict[obj1],self.objectDict[obj2])
                else:
                    if self.scene_graph.has_edge(self.objectDict[obj1],self.objectDict[obj2]):
                        self.scene_graph.remove_edge(self.objectDict[obj1],self.objectDict[obj2])

    def get_scene_graph(self):
        return self.scene_graph
    
    @staticmethod
    def draw_graph(G,ax):
        ax.clear()
        pos = nx.spring_layout(G)
        nx.draw(G,pos,with_labels=True,node_color='skyblue',edge_color='gray',ax=ax)
        plt.draw()
        

    def timer_callback(self):
        msg= String()
        msg.data = "Hi from observer"
        self.publisher_.publish(msg)
        self.define_relations()
        self.draw_graph(self.scene_graph,self.ax)




def main():
    rclpy.init()
    plt.ion()
    observerNode = Observer()
    rclpy.spin(observerNode)

    plt.ioff()
    plt.show()
    observerNode.destroy_node()
    rclpy.shutdown()
if __name__=='__main__':
    main()