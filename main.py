import streamlit as st
import jinja2

def if_none(s):
    return "" if (not s or s in ["", "None", None]) else str(s)


def table_row(col1: str, col2: str) -> str:
    return f"<tr><td>{col1}</td><td>{if_none(col2)}</td></tr>"


def generate_boilerplate_table(charges, onus, record, outstanding, releases, grounds, orders):
    boilerplate_table = (
        "<style>td:first-child {min-width: 95px;font-style:italic;} td {vertical-align:top;}</style><table>"
    )
    boilerplate_table += table_row("Charges:", charges.replace("\n", ";"))
    boilerplate_table += table_row("Onus:", onus)
    boilerplate_table += table_row("Record:  ", record)
    boilerplate_table += table_row("O/S Charges:", outstanding)
    if releases:
        boilerplate_table += table_row("Releases:", releases)
    boilerplate_table += table_row("Grounds:", grounds)
    if orders:
        boilerplate_table += table_row("Orders:", orders)
    boilerplate_table += "</table>"
    return boilerplate_table

def generate_flag(arrest_time):
    if not arrest_time:
        return
    return "".join(
            [
                "\n<strong>Section 503 compliance</strong>",
                '<div style="border:1px dotted red;padding:1.5%;">',
                f"This accused was arrested yesterday at <b>{arrest_time}</b>.\n",
                "They <i>must</i> appear before a justice <i>before</i> that time today, to comply with s. 503.",
                "</div>\n",
                "<strong>Boilerplate info</strong>",
            ]
        )
def main():
    st.title("Generate Bail Position HTML")
    col1, col2, col3 = st.columns(3)
    name = col1.text_input("Name of Accused")
    age = col2.text_input("Age")
    charges = col3.text_input("Charges")
    col1, col2, col3 = st.columns(3)
    onus = col1.text_input("Onus")
    record = col2.text_input("Record")
    outstanding = col3.text_input("Outstanding Charges")
    col1, col2, col3 = st.columns(3)
    releases = col1.text_input("Releases")
    grounds = col2.text_input("Grounds of Concern")
    orders = col3.text_input("Orders Requested (516(2), 486.4, etc.)")
    if st.checkbox("Arrested yesterday?"):
        arrest_time = st.text_input("Arrest Time")
    else:
        arrest_time = None

    position = st.text_area("Bail Position",height=200)
    if st.checkbox("Include Public Notes"):
        publicNotes = st.text_area("Public Notes", height=100)
    else:
        publicNotes = ""

    if st.checkbox("Include Notes for Crown Only"):
        notes = st.text_area("Crown Notes", height=100)
    else:
        notes = ""
    if st.button("Generate HTML"):
        st.write("Click the overlapping squares symbol at the top right of the code block to copy the HTML.")
        with open("bail_position_template.html", "r") as f:
            template = jinja2.Template(f.read())
        html = template.render(
            name=name,
            age=age,
            boilerplate_table = generate_boilerplate_table(charges, onus, record, outstanding, releases, grounds, orders),
            position=position,
            notes=notes,
            publicNotes=publicNotes,
            flag = generate_flag(arrest_time)
        )
        st.code(html, language="html")
        st.write("To produce another position, reload the page in your browser.")
            

if __name__ == "__main__":
    main()