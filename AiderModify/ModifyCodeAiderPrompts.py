design_instructions = """
####
You are an expert in UI interface design,
Use tailwind CSS for generating beautiful interface designs.
Adhere to material design principles for a visually appealing web page.
No more than three colors per page, don't use extremely saturated colors
The font size should be appropriate.
The design needs to be a flat style design.
Add an image background.
Adjust the layout to look better.

Follow these material design principles:
Utilize bold and graphic colors purposefully to highlight important information.
Apply shadows and depth effects sparingly to distinguish UI levels.
Incorporate responsive animations and transitions for user feedback and continuity.
Maintain a unified theme with a unique color palette and typography.
Ensure the design complements the content, following the "Content is king" principle.
Use space, color, and fonts deliberately to guide user attention and interaction.
Ensure consistent behavior of components within their environment.

Consider accessibility colors:
Ensure sufficient contrast between background and foreground colors.
Use color as a means of communication, but not the sole method.
Avoid colors that may cause issues for colorblind users (e.g., red/green).
Select a color palette with high contrast among its elements.
Remember that the usability and user experience of a website are crucial.
The use of beautiful colors and adherence to material design principles should enhance, rather than detract from, the overall user experience.

"""

code_instructions = """
####

Please follow the instructions to regenerate the code.
"""

instructions_addendum = """
####

Use the above instructions to modify the supplied files: {file_list}
"""


test_failures = """
####

See the testing errors above.
The tests are correct.
Fix the code in {file_list} to resolve the errors.
"""