from dataclasses import dataclass
import scripts.BasicChange as bc

@dataclass
class DiffRes:
    changes : list[bc.BasicChange]
    
    def isEmpty(self) -> bool:
        return len(self.changes) == 0;

    def addChange(self, change : bc.BasicChange):
        self.changes.append(change)

    #Changes Methods
    def getAdded(self) -> list[bc.ComponentAdded]:
        return [added for added in self.changes if isinstance(added,bc.ComponentAdded)]
    
    def getRemoved(self) -> list[bc.ComponentRemoved]:
        return [removed for removed in self.changes if isinstance(removed, bc.ComponentRemoved)]    

    def getModified(self) -> list[bc.ComponentModified]:
        return [modified for modified in self.changes if isinstance(modified, bc.ComponentModified)]

    def filterFile(self) -> list["DiffRes"]:
        groupedbyfile: dict[str, list[bc.BasicChange]] = {}

        for change in self.changes:
            fileorigin = change.origin
            if fileorigin not in groupedbyfile:
                groupedbyfile[fileorigin] = []
            groupedbyfile[fileorigin].append(change)
        return [DiffRes(changes=changes_list) for changes_list in groupedbyfile.values()] 
    
    def groupByComponent(self) -> list["DiffRes"]:
        grouped: dict[str, list[bc.BasicChange]] = {}

        for change in self.changes:
            ref = change.reference

            if ref not in grouped:
                grouped[ref] = []
            grouped[ref].append(change)
        return [DiffRes(changes=changes_list) for changes_list in grouped.values()]

    #Component Methods
    def hasComponent(self) -> bool:
        return self.changes is not None
    
    #Idea for possible Implementation 
    #def getOnlyWires(self) -> list[bc.BasicChange]: # When user only wants to see changes that were made with wires
        #pass

    #def sortChanges(self) -> list[bc.BasicChange]:  # Sorts Components in a specific manner
        #pass
