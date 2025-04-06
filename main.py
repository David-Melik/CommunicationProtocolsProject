import yaml
import argparse

# python -m pip install rich
from rich.console import Console
from rich.prompt import Prompt
from rich.style import Style
from rich.table import Table

# Initialize the console for rich text output
console = Console()


def protocol_read(file_path):
    with open(file_path, "r") as file:
        content = yaml.safe_load(file)  # Load and parse the YAML file

        # Create a table for displaying the settings
        table_protocol = Table(show_header=True, header_style="bold cyan")
        table_protocol.add_column("State", style="dim", width=20)
        table_protocol.add_column("Event")
        table_protocol.add_column("Transition")

        row_content = []
        protocol_name = content.get("protocol_name", [])
        console.print(f"Protocol: {protocol_name}", style="bold cyan")
        states = content.get("states", [])
        transitions = content.get("transitions", [])

        for state in states:
            # Create the row content for each state
            row_content = [state]

            # Find all transitions where the 'from' state is the current state
            transition_info = []
            event_info = []
            for transition in transitions:
                if transition.get("from") == state:
                    transition_info.append(
                        f"({transition.get('from')} -> {transition.get('to')})"
                    )
                    event_info.append(transition.get("event", "N/A"))

            # If there are transitions, join them with a comma. Otherwise, display "No transitions"
            if transition_info:
                row_content.append(" | ".join(event_info))
                row_content.append(" | ".join(transition_info))

            else:
                row_content.append("No transitions")
                row_content.append("No event")

            # Add the row to the table
            table_protocol.add_row(*row_content)

        # Print the table with the settings
        console.print(table_protocol)


def validate_protocol_file(file_path):
    try:
        with open(file_path, "r") as file:
            content = yaml.safe_load(file)

        # Check for required keys
        required_keys = ["protocol_name", "states", "transitions"]
        for key in required_keys:
            if key not in content:
                console.print(f"[bold red]Error:[/bold red] Missing key: {key}")
                return False

        # Check if states is a non-empty list
        states = content["states"]
        if not isinstance(states, list) or len(states) < 1:
            console.print(
                "[bold red]Error:[/bold red] States should be a non-empty list"
            )
            return False

        # Check if transitions is a non-empty list
        transitions = content["transitions"]
        if not isinstance(transitions, list) or len(transitions) < 1:
            console.print(
                "[bold red]Error:[/bold red] Transitions should be a non-empty list"
            )
            return False

        # Check for duplicates in states
        if len(states) != len(set(states)):
            console.print("[bold red]Error:[/bold red] Duplicate states found")
            return False

        # Check for states with no transitions
        state_set = set(states)
        state_with_no_transitions = [
            state
            for state in states
            if not any(t["from"] == state for t in transitions)
        ]
        if state_with_no_transitions:
            console.print(
                f"[bold red]Error:[/bold red] States with no transitions: {', '.join(state_with_no_transitions)}"
            )
            return False

        # Check each transition for valid from/to states and non-empty events
        for transition in transitions:
            if not all(k in transition for k in ["from", "to", "event"]):
                console.print(
                    "[bold red]Error:[/bold red] Each transition must contain 'from', 'to', and 'event'"
                )
                return False
            if transition["from"] not in state_set or transition["to"] not in state_set:
                console.print(
                    f"[bold red]Error:[/bold red] Invalid state in transition: {transition}"
                )
                return False
            if not isinstance(transition["event"], str) or not transition["event"]:
                console.print(
                    f"[bold red]Error:[/bold red] Event must be a non-empty string in transition: {transition}"
                )
                return False

        # If all checks pass
        return True

    except Exception as e:
        console.print(f"[bold red]Error reading protocol file:[/bold red] {e}")
        return False


def settings_read(file_path):

    # Print the settings in a table
    with open(file_path, "r") as file:
        content = yaml.safe_load(file)  # Load and parse the YAML file

        # Create a table for displaying the settings
        console.print(f"Imported Settings:", style="bold cyan")
        table_settings = Table(show_header=True, header_style="bold cyan")
        table_settings.add_column("Machine name", style="dim", width=12)
        table_settings.add_column("Inital state")

        for machine, machine_data in content.items():
            initial_state = ", ".join(machine_data["Initial_state"])
            row_content = [machine, initial_state]
            # Add row to the table
            table_settings.add_row(*row_content)

        # Print the table with the settings
        console.print(table_settings)


def validate_settings_file(file_path):
    try:
        with open(file_path, "r") as file:
            content = yaml.safe_load(file)

        # Check if there are at least two machines
        if len(content) < 2:
            raise ValueError(
                "There must be at least two machines in the settings file."
            )

        # Check that every machine has at least one initial state
        for machine_name, machine_data in content.items():
            if "Initial_state" not in machine_data:
                raise ValueError(
                    f"Machine '{machine_name}' is missing an 'Initial_state'."
                )
            if not machine_data["Initial_state"]:
                raise ValueError(
                    f"Machine '{machine_name}' has no initial state defined."
                )
        # If all checks pass
        return True, "Settings file is valid."

    except ValueError as e:
        console.print(f"[bold red]Error in settings files[/bold red]: {e}")
        return False


def read_yaml_file(file_path):
    # Open the YAML file and read its content
    with open(file_path, "r") as file:
        content = yaml.safe_load(file)  # Load and parse the YAML file

        # Print the content of the YAML file
        console.print("\nContent of the file:", style="bold cyan")
        console.print(content, style="italic green")


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Simulator, executor for N protocol entities"
    )

    parser.add_argument(
        "-p",
        "--protocol",
        type=str,
        help="Path to the protocol file (in YAML extension)",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        help="Path to the settings settings file (in YAML extension)",
        required=True,
    )

    # Parse the arguments
    args = parser.parse_args()

    try:
        # Check if the protocol file and settings file are the same
        if args.protocol == args.settings:
            raise ValueError("Protocol file and settings file cannot be the same.")
        # Validate both files have the correct extension
        for file_path in [args.protocol, args.settings]:
            if not file_path.endswith((".yaml", ".yml")):
                raise ValueError(
                    f"The file '{file_path}' is not a valid YAML file (must have .yaml or .yml extension)."
                )

        # Read the protocol YAML file
        if validate_protocol_file(args.protocol) and validate_settings_file(
            args.settings
        ):
            protocol_read(args.protocol)
            settings_read(args.settings)

    except ValueError as e:
        # Catch invalid file extension or other ValueErrors
        console.print(f"[bold red]Error[/bold red]: {e}")
    except Exception as e:
        # Catch any unexpected errors
        console.print(f"[bold red]Error[/bold red]: {e}")


if __name__ == "__main__":
    main()
