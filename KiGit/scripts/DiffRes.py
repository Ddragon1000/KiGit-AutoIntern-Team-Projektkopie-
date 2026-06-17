from dataclasses import dataclass
import BasicChange as bc

@dataclass
class DiffRes:
    changes : list[bc.BasicChange]

    def addChange(self, change : bc.BasicChange):
        self.changes.append(change)

    #Changes Methods
    def getAdded(self) -> list[bc.ComponentAdded]:
        return [added for added in self.changes if isinstance(added,bc.ComponentAdded)]
    
    def getRemoved(self) -> list[bc.ComponentRemoved]:
        pass    

    def getModified(self) -> list[bc.ComponentModified]:
        pass

    #Component Methods
    def hasComponent(self) -> bool:
        return self.changes is not None
    
    #Idea for possible Implementation 
    def getOnlyWires(self) -> list[bc.BasicChange]: # When user only wants to see changes that were made with wires
        pass

    def sortChanges(self) -> list[bc.BasicChange]:  # Sorts Components in a specific manner
        pass
