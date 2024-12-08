#Name : Noura Manassra
#ID : 1212359
#Section : 5
import os #it's important to deal with th current os, for example to deal with
          #with the existing paths
import subprocess #to use the shell commands in pythin
import re  # Import the 're' module,  to remove some letters from a string
import glob # for mathcing lined
import xml.etree.ElementTree as ET # to generate the xml files, and i used the tree here
                                     #so each node at the tree will act as the command

# to get the recommendations for each command
grep_recommendations = [ "sed", "cut", "sort", "awk"]
sed_recommendations = ["grep", "cut", "sort", "awk"]
cut_recommendations = ["grep", "sed", "sort", "awk"]
awk_recommendations = ["grep", "sed", "cut", "sort"]
sort_recommendations = ["grep", "sed", "cut", "awk"]
top_recommendations = ["du", "df"]
du_recommendations = ["top","df"]
df_recommendations = ["top", "du"]
ps_recommendations = ["kill"]
kill_recommendations = ["ps"]
chown_recommendations = ["chmod"]
chmod_recommendations = ["chown"]
ls_recommendations = ["mv", "rm", "cp", "cd", "mkdir", "pwd", "rmdir"]
mv_recommendations = ["ls", "rm", "cp", "cd", "mkdir", "pwd", "rmdir"]
rm_recommendations = ["ls", "mv", "cp", "cd", "mkdir", "pwd", "rmdir"]
cp_recommendations = ["ls", "mv", "rm", "cd", "mkdir", "pwd", "rmdir"]
cd_recommendations = ["ls", "mv", "rm", "cp", "mkdir", "pwd", "rmdir"]
mkdir_recommendations = ["ls", "mv", "rm", "cp", "cd", "pwd", "rmdir"]
pwd_recommendations = ["ls", "mv", "rm", "cp", "cd", "mkdir", "rmdir"]
rmdir_recommendations = ["ls", "mv", "rm", "cp", "cd", "mkdir", "pwd"]

command_recommendations = {}


# this dictionary used to store the command name,
# with its data which will be used as values
class CommandManualGenerator:
    def __init__(self, my_commands_file="commands.txt"):
        self.commands_file_path = my_commands_file
        self.command_recommendations = {}
        self.last_search = None

    def create_manuals_directory(self):
        # here I need to create a directory for manuals
        try:
            os.makedirs("CommandManuals", exist_ok=True)
        # the first parameter here is the name of the directory to be created.
        # the second parameter here ensures that the function does not raise an
        # error if the directory already exists.
        except OSError as error:
            # so then the except block is executed if
            # an OSError occurs in the try block.
            print(f"Error while creating directory for Manuals: {error}")
            exit(1)

    def read_commands_from_file(self):
        # Check if the file exists
        if not os.path.exists(self.commands_file_path):
            # If the file does not exist, this line prints an error message indicating
            # that the specified file is not found. It uses an f-string to include the
            # filename in the error message.
            print(f"Error: File '{self.commands_file_path}' not found!")
            exit(1)

        with open(self.commands_file_path, "r") as commands_file:
            return [command.strip() for command in commands_file]

    def generate_manual_for_command(self, command):
        description = self.get_command_description(command)
        if not description:
            print(f"Error: Failed to retrieve description for command {command}")
            return

        first_five_lines = "\n".join(description.splitlines()[:5])
        # it keeps only the first five lines of the original string and discards the rest.
        version = subprocess.getoutput(f"{command} --version")
        example = self.get_command_example(command)
        try:
            execute_example = subprocess.run(example, shell=True, check=True, capture_output=True,
                                             text=True).stdout.strip()
        except subprocess.CalledProcessError as e:
            execute_example = f"Error executing example: {e}"
        related_commands = self.get_related_commands(command)
        self.command_recommendations[command] = related_commands
        self.write_manual(command, first_five_lines, version, example, execute_example, related_commands)
        print(f"Manual generated for {command}")

    # this function which will be getting the description for each command
    def get_command_description(self, command):
        # this is useful because I have a long expression that does not fit in one
        # line and I want to split it over multiple lines for readability
        description = subprocess.run(["man", command], capture_output=True, text=True).stdout.split("DESCRIPTION")[1].split(
            "OPTIONS")[0]
        description = ' '.join(description.splitlines()[:5])
        # Get the example for the command
        example = self.get_command_example(command)

        # Get the version for the command
        version = subprocess.getoutput(f"{command} --version")

        # Get related commands
        related_commands = self.get_related_commands(command)
        command_manual = CommandManual(
            command,
            description,
            version,  # Include the obtained version
            example,  # Include the obtained example
            example,
            related_commands
        )

        xml_string = XmlSerializer.serialize(command_manual)
        # capture_output=True means that the standard output and standard error
        # streams of the external command are captured and stored in the stdout
        # and stderr attributes of the returned CompletedProcess object
        if "error" in description.lower():
            return None
        # remove leading and trailing whitespace
        return description.strip()

    # this function which will get the examples for each command
    def get_command_example(self, command):
        examples = {
            "ls": "ls",
            "mv": "touch File1 && mv File1 File2 && ls && rm File2",
            "rm": "touch DeleteMe && ls && rm DeleteMe && ls",
            "cp": "echo 'NouraManassra' > SourceFile && cp SourceFile DestinationFile && ls && rm SourceFile DestinationFile",
            "cd": "mkdir ExampleDirectory && cd ExampleDirectory && pwd && cd .. && rmdir ExampleDirectory",
            "mkdir": "mkdir NewDirectory && ls && rmdir NewDirectory",
            "rmdir": "mkdir TempDir && ls && rmdir TempDir && ls",
            "pwd": "pwd",
            "chmod": "touch MyFile && chmod 755 MyFile && ls && rm MyFile && ls",
            "chown": "touch OwnerFile && chown username:groupname OwnerFile && ls && rm OwnerFile",
            "ps": "ps",
            "df": "df",
            "du": "du",
            "kill": "echo 'Hello' > KillMeFile; ps aux | grep 'KillMeFile' | awk '{print $2}' | xargs kill -9; rm KillMeFile",
            "top": "top -n 1 -b",
            "grep": "echo 'Search for this' > SearchFile && grep 'Search' SearchFile && rm SearchFile",
            "sed": "echo 'Replace this' > ReplaceFile && sed -i 's/Replace/Changed/' ReplaceFile && cat ReplaceFile && rm ReplaceFile",
            "cut": "echo '1,NOURAMANASSRA' > CutFile && cut -d',' -f2 CutFile && rm CutFile",
            "sort": "echo -e '3\n1\n2' > UnsortedFile && sort UnsortedFile && rm UnsortedFile",
            "awk": "echo 'Name, Age, Grade\nNOURA, 20, A\nMANASSRA, 22, B' > DataFile && awk -F', ' '{print $1}' DataFile && rm DataFile",
        }
        return examples.get(command, command)

    def get_related_commands(self, command):
        try:  # note here to use the shell commands we are supposed to use the subprocess
            result = subprocess.run(["bash", "-c", f"compgen -c | grep '{command}'"], capture_output=True,
                                    text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting related commands: {e}")
            return None

    def write_manual(self, command, description, version, example, execute_example, related_commands):
        with open(f"CommandManuals/{command}.xml", "w") as command_manual:
            command_manual.write(f'<Manuals>\n')
            command_manual.write(f'  <CommandManual>\n')
            command_manual.write(f'    <CommandName>{command}</CommandName>\n')
            command_manual.write(f'    <CommandDescription>{description}</CommandDescription>\n')
            command_manual.write(f'    <VersionHistory>{version}</VersionHistory>\n')
            command_manual.write(f'    <Example>{example}</Example>\n')
            command_manual.write(f'    <ExecuteExample>{execute_example}</ExecuteExample>\n')
            command_manual.write(f'    <RelatedCommands>{related_commands}</RelatedCommands>\n')
            command_manual.write(f'  </CommandManual>\n')
            command_manual.write(f'</Manuals>\n')

    def generate_manuals(self):
        self.create_manuals_directory()
        commands = self.read_commands_from_file()
        for command in commands:
            self.generate_manual_for_command(command)
        print("All Manuals are generated!")

    ######################### N O W  T H E  V E R I F I C A T I O N ########################
    def verify_manual(self, command):
        CommandManual = f"CommandManuals/{command}.xml"
        # create an XML file that contains the manual for the given command.
        # to check whether the file path stored in the variable CommandManual
        # exists or not. This method returns True if the path refers to an e
        # xisting file or directory, and False otherwise
        if not os.path.exists(CommandManual):
            print(f"Error: The Manual for {CommandManual} does not exist.")
            exit(1)

        with open(CommandManual, "r") as manual_file:
            xml_content = manual_file.read()
        # it uses the read method of the file object to read the entire file as a string
        # and store it in the variable xml_content. This variable contains the XML data
        # that represents the manual for the given command.

        verification_failed = False  # variable to track verification failure

        start_tag = "<CommandDescription>"
        end_tag = "</CommandDescription>"
        # it defines two variables, start_tag and end_tag, which are strings that contain the
        # opening and closing tags of an XML element named CommandDescription.
        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)
        # search for the first occurrence of the start_tag and the end_tag in the string,
        # and returns their indices.
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find CommandDescription tags in {CommandManual}.")
            exit(1)

        # assign ActualD to the content between the CommandDescription tags, and strip any whitespace
        ActualD = xml_content[start_index + len(start_tag):end_index].strip()

        # find the position of the closing tag of CommandDescription
        close_tag_index = xml_content.find("</CommandDescription>", end_index)

        # if the closing tag is not found, print an error message and exit the program
        if close_tag_index == -1:
            print(f"Error: Unable to find the closing tag of CommandDescription in {CommandManual}.")
            exit(1)

        # retrieve ExpectedD from the XML content by calling the get_command_description method
        ExpectedD = self.get_command_description(command)

        # if ExpectedD and ActualD are not equal, set verification_failed to True and print an error message
        if ExpectedD != ActualD:
            verification_failed = True
            print(f"Error: The Description is not verified for {command}!")
            print(f"Expected Description: {ExpectedD}")
            print(f"Actual Description:   {ActualD}")

        # assign start_tag and end_tag to the opening and closing tags of ExecuteExample
        start_tag = "<ExecuteExample>"
        end_tag = "</ExecuteExample>"

        # find the position of the start_tag and the end_tag in the XML content
        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)

        # if either of the tags is not found, or the end_tag comes before the start_tag, print an error message and exit the program
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find Example tags in {CommandManual}.")
            exit(1)

        # assign ActualExample to the content between the ExecuteExample tags, and strip any whitespace
        ActualExample = xml_content[start_index + len(start_tag):end_index].strip()

        # find the position of the closing tag of ExecuteExample
        close_tag_index = xml_content.find(end_tag, end_index)

        # if the closing tag is not found, print an error message and exit the program
        if close_tag_index == -1:
            print(f"Error: Unable to find the closing tag of Example in {CommandManual}.")
            exit(1)

        # retrieve ExpectedExample from the XML content by calling the get_command_example method and executing the command using subprocess
        ExpectedExample = subprocess.getoutput(self.get_command_example(command))

        # if ExpectedExample and ActualExample are not equal, set verification_failed to True and print an error message
        if ExpectedExample != ActualExample:
            verification_failed = True
            print(f"Error: The Example is not verified for {command}!")
            print(f"Expected Example: {ExpectedExample}")
            print(f"Actual Example:   {ActualExample}")

        # assign start_tag and end_tag to the opening and closing tags of VersionHistory
        start_tag = "<VersionHistory>"
        # Assign end_tag to the closing tag of VersionHistory
        end_tag = "</VersionHistory>"

        # Find the position of the start_tag and the end_tag in the XML content
        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)

        # If either of the tags is not found, or the end_tag comes before the start_tag, print an error message and exit the program
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find VersionHistory tags in {CommandManual}.")
            exit(1)

        # Assign ActualVersionHistory to the content between the VersionHistory tags, and strip any whitespace
        ActualVersionHistory = xml_content[start_index + len(start_tag):end_index].strip()

        # Find the position of the closing tag of VersionHistory
        close_tag_index = xml_content.find(end_tag, end_index)

        # If the closing tag is not found, print an error message and exit the program
        if close_tag_index == -1:
            print(f"Error: Unable to find the closing tag of VersionHistory in {CommandManual}.")
            exit(1)

        # Retrieve ExpectedVersionHistory from the XML content by executing the command with the --version option using subprocess
        ExpectedVersionHistory = subprocess.getoutput(f"{command} --version")

        # If ExpectedVersionHistory and ActualVersionHistory are not equal, set verification_failed to True and print an error message
        if ExpectedVersionHistory != ActualVersionHistory:
            verification_failed = True
            print(f"Error: The VersionHistory is not verified for {command}!")
            print(f"Expected VersionHistory: {ExpectedVersionHistory}")
            print(f"Actual VersionHistory:   {ActualVersionHistory}")

        # Assign start_tag and end_tag to the opening and closing tags of RelatedCommands
        start_tag = "<RelatedCommands>"
        end_tag = "</RelatedCommands>"

        # Find the position of the start_tag and the end_tag in the XML content
        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)

        # If either of the tags is not found, or the end_tag comes before the start_tag, print an error message and exit the program
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find RelatedCommands tags in {CommandManual}.")
            exit(1)

        # Assign ActualRelatedCommands to the content between the RelatedCommands tags, and strip any whitespace
        ActualRelatedCommands = xml_content[start_index + len(start_tag):end_index].strip()

        # Find the position of the closing tag of RelatedCommands
        close_tag_index = xml_content.find(end_tag, end_index)

        # If the closing tag is not found, print an error message and exit the program
        if close_tag_index == -1:
            print(f"Error: Unable to find the closing tag of RelatedCommands in {CommandManual}.")
            exit(1)

        # Retrieve Expected RelatedCommands from the XML content
        ExpectedRelatedCommands = self.get_related_commands(command)

        if ExpectedRelatedCommands != ActualRelatedCommands:
            verification_failed = True
            print(f"Error: The RelatedCommands are not verified for {command}!")
            print(f"Expected RelatedCommands: {ExpectedRelatedCommands}")
            print(f"Actual RelatedCommands:   {ActualRelatedCommands}")

        if not verification_failed:
            print(f"Verification successful for {command}")

    def verify_manuals(self):
        commands = self.read_commands_from_file()
        for command in commands:
            self.verify_manual(command)
        print("Verification Is Done !")

    def search_command_manual(self, answer1):
        self.last_search = answer1
        command_file = f"CommandManuals/{answer1}.xml"
        if os.path.exists(command_file):
            print(f"Command manual for '{answer1}' exists:")
            while True:
                print("\nSelect a part to display:")
                print("1. Full Manual")
                print("2. Command Description")
                print("3. Version History")
                print("4. Example")
                print("5. Execute Example")
                print("6. Related Commands")
                print("7. Go Back to Main Menu")

                part_choice = input("Enter your choice (1-7): ")

                if part_choice == "1":
                    with open(command_file, "r") as file:
                        print(file.read())
                elif part_choice == "2":
                    self.display_part(command_file, "CommandDescription")
                elif part_choice == "3":
                    self.display_part(command_file, "VersionHistory")
                elif part_choice == "4":
                    self.display_part(command_file, "Example")
                elif part_choice == "5":
                    self.display_part(command_file, "ExecuteExample")
                elif part_choice == "6":
                    self.display_part(command_file, "RelatedCommands")
                elif part_choice == "7":
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 7.")
        else:
            files = glob.glob("CommandManuals/*.xml")
            matching_files = [file for file in files if answer1 in os.path.basename(file)]

            if matching_files:
                print(f"Found matches for '{answer1}' in the following files:")
                for match in matching_files:
                    print(os.path.basename(match))
            else:
                print("No matches found! Files in Command Manuals:")
                for file in os.listdir("CommandManuals"):
                    print(file)

    def display_part(self, command_file, part_tag):
        with open(command_file, "r") as file:
            xml_content = file.read()

        start_tag = f"<{part_tag}>"
        end_tag = f"</{part_tag}>"

        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)

        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find {part_tag} tags in {command_file}.")
            return

        part_content = xml_content[start_index + len(start_tag):end_index].strip()
        print(f"\n{part_tag}:\n{part_content}")

    def get_recommendations(self, command):
        command_recommendations_key = f"{command}_recommendations"
        if command_recommendations_key in globals():
            return globals()[command_recommendations_key]
        else:
            return []

    def recommend_commands(self, last_search):
        if last_search:
            recommendations = self.get_recommendations(last_search)
            if recommendations:
                print(f"Recommendations for '{last_search}':")
                for recommendation in recommendations:
                    print(f"- {recommendation}")
            else:
                print(f"No recommendations found for '{last_search}'.")

# the CommandManual class is used to represent the data of a command manual.
class CommandManual:
    def __init__(self, command_name, command_description, version_history, example, execute_example, related_commands):
        self.command_name = command_name
        self.command_description = command_description
        self.version_history = version_history
        self.example = example
        self.execute_example = execute_example
        self.related_commands = related_commands


# the XmlSerializer class is used to serialize a CommandManual object to an XML string.
class XmlSerializer:
    @staticmethod
    def serialize(command_manual):
        root = ET.Element("Manuals")
        command_element = ET.SubElement(root, "CommandManual")
        ET.SubElement(command_element, "CommandName").text = command_manual.command_name
        ET.SubElement(command_element, "CommandDescription").text = command_manual.command_description
        ET.SubElement(command_element, "VersionHistory").text = command_manual.version_history
        ET.SubElement(command_element, "Example").text = command_manual.example
        ET.SubElement(command_element, "ExecuteExample").text = command_manual.execute_example
        ET.SubElement(command_element, "RelatedCommands").text = command_manual.related_commands

        xml_string = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return xml_string


# the Main function is used to instantiate the CommandManualGenerator class
# and call its methods to generate and verify command manuals.
if __name__ == "__main__":
    command_manual_generator = CommandManualGenerator()

    while True:
        print("\nMenu:")
        print("1. Generate Manuals")
        print("2. Verify Manuals")
        print("3. Search Command Manual")
        print("4. Recommend Commands")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            command_manual_generator.generate_manuals()
        elif choice == "2":
            command_manual_generator.verify_manuals()
        elif choice == "3":
            answer1 = input("Enter the command name or topic: ")
            command_manual_generator.search_command_manual(answer1)
        elif choice == "4":
            command_manual_generator.recommend_commands(command_manual_generator.last_search)
        elif choice == "5":
            print("allah ma3ak!!")
            exit(0)
        else:
            print("dear user, u entered wrong option")