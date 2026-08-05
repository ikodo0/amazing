from .component import Component
import sys


class Screen:
    def __init__(self, *comps: Component) -> None:
        self.components = []
        self.components.extend(comps)

    def mount(self, component: Component) -> None:
        self.components.append(component)

    def unmount(self, component: Component) -> None:
        try:
            self.components.remove(component)
        except ValueError as e:
            print(f"ERROR | Failed to remove unknown component: "
                  f"{component.__class__.__name__} from Screen.\n"
                  f"{e}",
                  file=sys.stderr)

    def on_enter(self) -> None:
        ...

    def on_exit(self) -> None:
        ...
