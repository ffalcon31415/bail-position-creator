import streamlit as st
import jinja2
import dataclasses
import pandas as pd
from pathlib import Path


@dataclasses.dataclass
class PleaPosition:
    name: str | None = ""
    scopeNumbers: str | None = ""
    counts: str | None = ""
    election: str | None = "Summary"
    visRequired: bool = True
    additionalFacts: str | None = ""
    position: str | None = ""
    crownNotes: str | None = ""
    deadline: str | None = ""


def generate_html_table(
    scope_numbers: list[str], counts: list[str], padding: int = 5
) -> str:
    """
    Generate an HTML table with scope_numbers and counts as columns.

    Args:
        scope_numbers (list): List of strings representing scope numbers.
        counts (list): List of strings representing counts.
        padding (int, optional): Padding value in pixels for cell padding. Default is 5.

    Returns:
        str: HTML code for the generated table.

    """
    # Check if the lengths of the input lists are the same
    if len(scope_numbers) != len(counts):
        msg = "The input lists must have the same length."
        raise ValueError(msg)

    # Generate the HTML table
    table_html = "<table border='1'>"
    table_html += f"  <tr><th style='padding: {padding}px; font-weight: bold;'>Scope Number</th><th style='padding: {padding}px; font-weight: bold;'>Count(s)</th> </tr>"
    for scope, count in zip(scope_numbers, counts, strict=True):
        table_html += f"  <tr><td style='padding: {padding}px;; text-align: center'>{scope}</td><td style='padding: {padding}px;'>{count}</td>  </tr>"
    table_html += "</table>"

    return table_html


def generate_plea_position_html(plea_position: PleaPosition) -> str:
    if not plea_position.scopeNumbers or not plea_position.counts:
        return ""
    text = "Counsel or accused to notify the Crown in advance if this is to be a guilty plea so that VIS can be requested in a timely way, consistent with the Victims' Bill of Rights."
    vis = (
        f"""<br><span style="border:1px dotted red;padding:1%;"><strong>VIS required.</strong></span><br><br><span>{text}</span><br>"""
        if plea_position.visRequired
        else ""
    )
    html_table = generate_html_table(plea_position.scopeNumbers, plea_position.counts)
    additional_facts = (
        "<br><strong>Additional facts alleged: </strong><br>"
        + plea_position.additionalFacts
        + "<br>"
        if plea_position.additionalFacts
        else ""
    )
    miscellaneous_notes = (
        "<br><strong>Miscellaneous Notes for Crown only:</strong><br>"
        + plea_position.crownNotes
        if plea_position.crownNotes
        else ""
    )

    with Path("plea_position.html").open() as file_:
        template = jinja2.Template(file_.read())
    return template.render(
        plea_position=plea_position,
        vis=vis,
        html_table=html_table,
        additional_facts=additional_facts,
        miscellaneous_notes=miscellaneous_notes,
    )


def main():
    st.title("Generate Plea Position")
    st.write(
        "Do not input any sensitive or privileged information into this form. This app is not secure."
    )
    name = st.text_input("Name of Accused")
    election = st.radio("Election:",["Summary", "Indictable"])
    visRequired = st.checkbox("VIS Required?", value=True)
    if st.checkbox("Include deadline for plea?"):
        deadline = st.text_input(
            "Deadline for plea",
            help="Enter the deadline for the plea offer, if applicable.",
        )       
    else:
        deadline = None
    df = pd.DataFrame(
        {
            "Scope Number": [
                "",
                
            ],
            "Counts for Plea": ["",],
        }
    )
    st.write("## Counts for Plea")
    st.write(
        "Enter the scope numbers and counts for plea. Leave blank if the accused is not pleading guilty to any counts.")
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,

        column_config={
            "Scope Number": st.column_config.TextColumn(
                "Scope Number", 
                help="Enter the scope number for each count.",
                max_chars=10,
                width="small",
                
            ),
            "Counts for Plea": st.column_config.TextColumn(
                "Counts the accused will plead guilty to (if any)",
                help="Enter the counts for plea corresponding to each scope number. Other counts will be read in and withdrawn, unless otherwise specified.",
                width="large",
            ),
        },
    )
    st.write("## Crown Plea Position")
    st.write(
        "Enter the Crown's plea position. Open position unless otherwise specified."
    )
    position = st.text_area(
        "## Crown Plea Position",
        height=200,
        value="Credit for time served to be noted at 1.5:1.\n",
        help="Enter the Crown's plea position. Open position unless otherwise specified.",
    )


    if st.checkbox("Include additional facts to be admitted?"):
        additionalFacts = st.text_area(
            "Additional Facts to be Admitted",
            height=100,
        )
    else:
        additionalFacts = ""
    if st.checkbox("Include Notes for Crown Only"):
        crownNotes = st.text_area("Crown Notes", height=100)
    else:
        crownNotes = ""

    ct = st.container(border=True)
    plea_position = PleaPosition(
        name=name,
        # Convert to string to avoid NoneType issues in rendering
        # This is a workaround for the dataclass not accepting None as a default value
        scopeNumbers=[str(x) for x in edited_df["Scope Number"].tolist()],
        counts=[str(x) if str(x) else "Read in and withdraw as above" for x in edited_df["Counts for Plea"].tolist()],
        election=election,
        visRequired=visRequired,
        additionalFacts=additionalFacts,
        position=position,
        crownNotes=crownNotes,
        deadline=deadline,
    )

    if ct.button("Generate Position"):
        html = generate_plea_position_html(plea_position)
        cont2 = st.container(border=True)
        cont2.write("### Results below!")
        cont2.write(
            "Click the overlapping squares symbol at the top right of the code block to copy the HTML."
        )
        cont2.code(html, language="html")

        cont2.write(
            "#### To generate another position, reload the page in your browser."
        )


if __name__ == "__main__":
    main()
