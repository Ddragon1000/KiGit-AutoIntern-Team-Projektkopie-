from dataclasses import dataclass

@dataclass
class BasicChange:      #Basic-Class for changes
    reference: str

#specific Changes that will be created and appended to DiffRes
@dataclass
class ComponentAdded(BasicChange):
    pass

@dataclass
class ComponentRemoved(BasicChange):
    pass

@dataclass
class ComponentModified(BasicChange):
    pass

@dataclass
class ComponentMoved(ComponentModified):
    positions : tuple

@dataclass
class ComponentValueChanged(ComponentModified):
    values : tuple
