#!/usr/bin/env python3
"""
Generate Python docstrings from Doxygen XML output.

This tool parses Doxygen XML documentation and generates a Python module
containing docstrings for libbifrost C functions, which can be applied
at runtime to the ctypes-generated wrappers.

Usage:
    python doxygen_to_pydoc.py --xml-dir ../docs/doxygen/xml --output bifrost/libbifrost_generated_docs.py
"""

import argparse
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DoxygenParser:
    """Parse Doxygen XML output and extract function documentation."""

    def __init__(self, xml_dir: str):
        self.xml_dir = Path(xml_dir)
        self.functions: Dict[str, dict] = {}

    def parse_all(self) -> Dict[str, dict]:
        """Parse all XML files in the Doxygen output directory."""
        if not self.xml_dir.exists():
            print(f"Warning: XML directory {self.xml_dir} does not exist")
            return {}

        # Parse the main index to find all compound files
        index_file = self.xml_dir / "index.xml"
        if index_file.exists():
            self._parse_index(index_file)
        else:
            # Fall back to parsing all XML files
            for xml_file in self.xml_dir.glob("*.xml"):
                if xml_file.name != "index.xml":
                    self._parse_compound_file(xml_file)

        return self.functions

    def _parse_index(self, index_file: Path):
        """Parse the Doxygen index.xml to find all documented files."""
        tree = ET.parse(index_file)
        root = tree.getroot()

        for compound in root.findall(".//compound"):
            kind = compound.get("kind")
            if kind in ("file", "group"):
                refid = compound.get("refid")
                compound_file = self.xml_dir / f"{refid}.xml"
                if compound_file.exists():
                    self._parse_compound_file(compound_file)

    def _parse_compound_file(self, xml_file: Path):
        """Parse a compound XML file for function documentation."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Warning: Failed to parse {xml_file}: {e}")
            return

        # Find all memberdef elements that are functions
        for memberdef in root.findall(".//memberdef[@kind='function']"):
            func_info = self._parse_function(memberdef)
            if func_info and func_info.get("name"):
                self.functions[func_info["name"]] = func_info

    def _parse_function(self, memberdef) -> Optional[dict]:
        """Parse a function's documentation from a memberdef element."""
        name_elem = memberdef.find("name")
        if name_elem is None or name_elem.text is None:
            return None

        name = name_elem.text

        # Only process bifrost functions
        if not name.startswith("bf"):
            return None

        info = {
            "name": name,
            "brief": "",
            "detailed": "",
            "params": [],
            "returns": "",
            "notes": [],
        }

        # Get brief description
        brief = memberdef.find("briefdescription")
        if brief is not None:
            info["brief"] = self._extract_text(brief).strip()

        # Get detailed description
        detailed = memberdef.find("detaileddescription")
        if detailed is not None:
            info["detailed"] = self._extract_detailed(detailed)

        # Get parameters
        for param in memberdef.findall(".//parameterlist[@kind='param']/parameteritem"):
            param_info = self._parse_param(param)
            if param_info:
                info["params"].append(param_info)

        # Get return value documentation
        for retval in memberdef.findall(".//simplesect[@kind='return']"):
            info["returns"] = self._extract_text(retval).strip()

        # Get notes
        for note in memberdef.findall(".//simplesect[@kind='note']"):
            note_text = self._extract_text(note).strip()
            if note_text:
                info["notes"].append(note_text)

        return info

    def _parse_param(self, param_item) -> Optional[Tuple[str, str]]:
        """Parse a parameter documentation item."""
        name_elem = param_item.find(".//parametername")
        desc_elem = param_item.find(".//parameterdescription")

        if name_elem is None:
            return None

        name = name_elem.text or ""
        desc = self._extract_text(desc_elem).strip() if desc_elem is not None else ""

        return (name, desc)

    def _extract_text(self, elem) -> str:
        """Extract all text content from an XML element."""
        if elem is None:
            return ""

        parts = []
        if elem.text:
            parts.append(elem.text)

        for child in elem:
            # Handle code/emphasis elements
            if child.tag in ("computeroutput", "emphasis", "bold"):
                if child.text:
                    parts.append(child.text)
            # Handle paragraph elements
            elif child.tag == "para":
                para_text = self._extract_text(child)
                if para_text:
                    parts.append(para_text)
            # Handle other elements recursively
            else:
                parts.append(self._extract_text(child))

            if child.tail:
                parts.append(child.tail)

        return " ".join(parts)

    def _extract_detailed(self, detailed_elem) -> str:
        """Extract detailed description, excluding param/return sections."""
        if detailed_elem is None:
            return ""

        parts = []
        for para in detailed_elem.findall("para"):
            # Skip if this paragraph contains param or return sections
            if para.find(".//parameterlist") is not None:
                continue
            if para.find(".//simplesect[@kind='return']") is not None:
                continue
            if para.find(".//simplesect[@kind='note']") is not None:
                continue

            text = self._extract_text(para).strip()
            if text:
                parts.append(text)

        return " ".join(parts)


def generate_docstring(func_info: dict) -> str:
    """Generate a Google-style Python docstring from function info."""
    lines = []

    # Brief description
    if func_info["brief"]:
        lines.append(func_info["brief"])

    # Detailed description
    if func_info["detailed"]:
        if lines:
            lines.append("")
        lines.append(func_info["detailed"])

    # Parameters
    if func_info["params"]:
        if lines:
            lines.append("")
        lines.append("Args:")
        for name, desc in func_info["params"]:
            if desc:
                lines.append(f"    {name}: {desc}")
            else:
                lines.append(f"    {name}")

    # Returns
    if func_info["returns"]:
        if lines:
            lines.append("")
        lines.append("Returns:")
        lines.append(f"    {func_info['returns']}")

    # Notes
    if func_info["notes"]:
        if lines:
            lines.append("")
        lines.append("Note:")
        for note in func_info["notes"]:
            lines.append(f"    {note}")

    return "\n".join(lines)


def generate_docs_module(functions: Dict[str, dict], output_path: str):
    """Generate the libbifrost_generated_docs.py module."""

    with open(output_path, 'w') as f:
        f.write('"""\n')
        f.write('Auto-generated docstrings for libbifrost C functions.\n')
        f.write('\n')
        f.write('This module is generated by doxygen_to_pydoc.py from Doxygen XML output.\n')
        f.write('Do not modify this file manually.\n')
        f.write('"""\n\n')

        f.write('DOCSTRINGS = {\n')

        for name, info in sorted(functions.items()):
            docstring = generate_docstring(info)
            if docstring:
                # Escape any triple quotes in the docstring
                docstring = docstring.replace('"""', '\\"\\"\\"')
                f.write(f'    "{name}": """{docstring}""",\n')

        f.write('}\n')

    print(f"Generated {len(functions)} docstrings to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Python docstrings from Doxygen XML output"
    )
    parser.add_argument(
        "--xml-dir",
        default="../docs/doxygen/xml",
        help="Path to Doxygen XML output directory"
    )
    parser.add_argument(
        "--output",
        default="bifrost/libbifrost_generated_docs.py",
        help="Output Python module path"
    )

    args = parser.parse_args()

    # Parse Doxygen XML
    parser = DoxygenParser(args.xml_dir)
    functions = parser.parse_all()

    if not functions:
        print("Warning: No documented functions found")
        # Still generate an empty module
        functions = {}

    # Generate the output module
    generate_docs_module(functions, args.output)


if __name__ == "__main__":
    main()
