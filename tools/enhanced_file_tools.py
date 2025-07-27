from typing import Any, Optional, Type
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field
import os
import glob
from pathlib import Path


class FileReadToolSchema(BaseModel):
    """Input for FileReadTool."""
    file_path: str = Field(..., description="Mandatory file full path to read the file")
    start_line: Optional[int] = Field(1, description="Line number to start reading from (1-indexed)")
    line_count: Optional[int] = Field(None, description="Number of lines to read. If None, reads the entire file")


class FileReadTool(BaseTool):
    """A tool for reading file contents.

    This tool inherits its schema handling from BaseTool to avoid recursive schema
    definition issues. The args_schema is set to FileReadToolSchema which defines
    the required file_path parameter. The schema should not be overridden in the
    constructor as it would break the inheritance chain and cause infinite loops.

    The tool supports two ways of specifying the file path:
    1. At construction time via the file_path parameter
    2. At runtime via the file_path parameter in the tool's input

    Args:
        file_path (Optional[str]): Path to the file to be read. If provided,
            this becomes the default file path for the tool.
        **kwargs: Additional keyword arguments passed to BaseTool.

    Example:
        >>> tool = FileReadTool(file_path="/path/to/file.txt")
        >>> content = tool.run()  # Reads /path/to/file.txt
        >>> content = tool.run(file_path="/path/to/other.txt")  # Reads other.txt
        >>> content = tool.run(file_path="/path/to/file.txt", start_line=100, line_count=50)  # Reads lines 100-149
    """

    name: str = "Read a file's content"
    description: str = "A tool that reads the content of a file. To use this tool, provide a 'file_path' parameter with the path to the file you want to read. Optionally, provide 'start_line' to start reading from a specific line and 'line_count' to limit the number of lines read."
    args_schema: Type[BaseModel] = FileReadToolSchema
    file_path: Optional[str] = None

    def __init__(self, file_path: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the FileReadTool.

        Args:
            file_path (Optional[str]): Path to the file to be read. If provided,
                this becomes the default file path for the tool.
            **kwargs: Additional keyword arguments passed to BaseTool.
        """
        if file_path is not None:
            kwargs["description"] = (
                f"A tool that reads file content. The default file is {file_path}, but you can provide a different 'file_path' parameter to read another file. You can also specify 'start_line' and 'line_count' to read specific parts of the file."
            )

        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(
        self,
        file_path: Optional[str] = None,
        start_line: Optional[int] = 1,
        line_count: Optional[int] = None,
    ) -> str:
        file_path = file_path or self.file_path
        start_line = start_line or 1
        line_count = line_count or None

        if file_path is None:
            return (
                "Error: No file path provided. Please provide a file path either in the constructor or as an argument."
            )

        try:
            with open(file_path, "r", encoding='utf-8', errors='ignore') as file:
                if start_line == 1 and line_count is None:
                    content = file.read()
                    return f"📄 **FILE CONTENT: {file_path}**\n\n```\n{content}\n```"

                start_idx = max(start_line - 1, 0)

                selected_lines = [
                    line
                    for i, line in enumerate(file)
                    if i >= start_idx and (line_count is None or i < start_idx + line_count)
                ]

                if not selected_lines and start_idx > 0:
                    return f"Error: Start line {start_line} exceeds the number of lines in the file."

                content = "".join(selected_lines)
                return f"📄 **FILE CONTENT: {file_path} (Lines {start_line}-{start_line + len(selected_lines) - 1})**\n\n```\n{content}\n```"
                
        except FileNotFoundError:
            return f"❌ Error: File not found at path: {file_path}"
        except PermissionError:
            return f"❌ Error: Permission denied when trying to read file: {file_path}"
        except Exception as e:
            return f"❌ Error: Failed to read file {file_path}. {str(e)}"


class FileWriteToolSchema(BaseModel):
    """Input for FileWriteTool."""
    file_path: str = Field(..., description="Mandatory file full path to write the content")
    content: str = Field(..., description="Content to write to the file")
    mode: str = Field("w", description="Write mode: 'w' for overwrite, 'a' for append")


class FileWriteTool(BaseTool):
    """A tool for writing content to files."""

    name: str = "Write content to a file"
    description: str = "A tool that writes content to a file. Provide 'file_path' for the target file and 'content' to write. Use 'mode' to specify write mode ('w' for overwrite, 'a' for append)."
    args_schema: Type[BaseModel] = FileWriteToolSchema

    def _run(
        self,
        file_path: str,
        content: str,
        mode: str = "w"
    ) -> str:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as file:
                file.write(content)
            
            return f"✅ Successfully wrote content to {file_path} (mode: {mode})"
            
        except PermissionError:
            return f"❌ Error: Permission denied when trying to write to file: {file_path}"
        except Exception as e:
            return f"❌ Error: Failed to write to file {file_path}. {str(e)}"


class FileSearchToolSchema(BaseModel):
    """Input for FileSearchTool."""
    search_query: str = Field(..., description="Search query to find in files")
    directory: str = Field(".", description="Directory to search in")
    file_pattern: str = Field("*", description="File pattern to search (e.g., '*.py', '*.txt')")


class FileSearchTool(BaseTool):
    """A tool for searching content in files."""

    name: str = "Search content in files"
    description: str = "A tool that searches for content in files within a directory. Provide 'search_query', 'directory' (optional), and 'file_pattern' (optional)."
    args_schema: Type[BaseModel] = FileSearchToolSchema

    def _run(
        self,
        search_query: str,
        directory: str = ".",
        file_pattern: str = "*"
    ) -> str:
        try:
            if not os.path.exists(directory):
                return f"❌ Error: Directory '{directory}' does not exist"
            
            # Build search pattern
            search_pattern = os.path.join(directory, f"**/{file_pattern}")
            files = glob.glob(search_pattern, recursive=True)
            
            if not files:
                return f"❌ No files found matching pattern '{file_pattern}' in directory '{directory}'"
            
            results = []
            query_terms = search_query.lower().split()
            
            for file_path in files:
                if os.path.isdir(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if all(term in content.lower() for term in query_terms):
                        rel_path = os.path.relpath(file_path, directory)
                        file_size = os.path.getsize(file_path)
                        
                        # Find line numbers where query appears
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            if all(term in line.lower() for term in query_terms):
                                matching_lines.append(i)
                        
                        results.append({
                            'file': rel_path,
                            'size': file_size,
                            'matching_lines': matching_lines[:5]  # Limit to first 5 matches
                        })
                        
                        if len(results) >= 10:  # Limit results
                            break
                            
                except Exception:
                    continue
            
            if not results:
                return f"❌ No files found containing '{search_query}' in directory '{directory}'"
            
            # Format results
            output = f"🔍 **FILE SEARCH RESULTS**\n"
            output += f"Query: '{search_query}'\n"
            output += f"Directory: '{directory}'\n"
            output += f"Pattern: '{file_pattern}'\n"
            output += f"Found: {len(results)} matching files\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"**{i}. {result['file']}** ({result['size']} bytes)\n"
                if result['matching_lines']:
                    output += f"   Matching lines: {', '.join(map(str, result['matching_lines']))}\n"
                output += "\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error during file search: {str(e)}"


# Create tool instances
file_read_tool = FileReadTool()
file_write_tool = FileWriteTool()
file_search_tool = FileSearchTool()


@tool("Enhanced File Reader")
def read_file_enhanced(file_path: str, start_line: int = 1, line_count: int = None) -> str:
    """
    Read file content with advanced features like line ranges and better formatting.
    
    Parameters:
        file_path (str): Full path to the file to read
        start_line (int): Line number to start reading from (1-indexed, default: 1)
        line_count (int): Number of lines to read (default: entire file)
    
    Returns:
        str: Formatted file content with syntax highlighting
    """
    return file_read_tool._run(file_path, start_line, line_count)


@tool("File Writer")
def write_file_enhanced(file_path: str, content: str, mode: str = "w") -> str:
    """
    Write content to a file with support for different write modes.
    
    Parameters:
        file_path (str): Full path to the file to write
        content (str): Content to write to the file
        mode (str): Write mode - 'w' for overwrite, 'a' for append (default: 'w')
    
    Returns:
        str: Success or error message
    """
    return file_write_tool._run(file_path, content, mode)


@tool("File Content Searcher")
def search_files_enhanced(search_query: str, directory: str = ".", file_pattern: str = "*") -> str:
    """
    Search for content in files with pattern matching and line number reporting.
    
    Parameters:
        search_query (str): Text to search for in files
        directory (str): Directory to search in (default: current directory)
        file_pattern (str): File pattern to search (e.g., '*.py', '*.txt', default: all files)
    
    Returns:
        str: Formatted search results with file paths and matching line numbers
    """
    return file_search_tool._run(search_query, directory, file_pattern)


@tool("File System Analyzer")
def analyze_file_system(directory: str = ".") -> str:
    """
    Analyze file system structure and provide detailed statistics.
    
    Parameters:
        directory (str): Directory to analyze (default: current directory)
    
    Returns:
        str: Detailed file system analysis report
    """
    try:
        if not os.path.exists(directory):
            return f"❌ Directory '{directory}' does not exist"
        
        # Collect file system data
        total_files = 0
        total_dirs = 0
        total_size = 0
        file_types = {}
        largest_files = []
        
        for root, dirs, files in os.walk(directory):
            total_dirs += len(dirs)
            
            for file in files:
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    # Track file types
                    ext = os.path.splitext(file)[1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
                    # Track largest files
                    largest_files.append((file_path, file_size))
                    
                except (OSError, PermissionError):
                    continue
        
        # Sort largest files
        largest_files.sort(key=lambda x: x[1], reverse=True)
        
        # Generate report
        output = f"📁 **FILE SYSTEM ANALYSIS**\n"
        output += f"Directory: '{directory}'\n\n"
        
        output += f"📊 **STATISTICS:**\n"
        output += f"• Total Files: {total_files:,}\n"
        output += f"• Total Directories: {total_dirs:,}\n"
        output += f"• Total Size: {total_size / (1024*1024):.2f} MB\n\n"
        
        if file_types:
            output += f"📄 **FILE TYPES:**\n"
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:10]:
                output += f"• {ext or 'no extension'}: {count:,} files\n"
            output += "\n"
        
        if largest_files:
            output += f"📦 **LARGEST FILES:**\n"
            for file_path, size in largest_files[:5]:
                rel_path = os.path.relpath(file_path, directory)
                size_mb = size / (1024*1024)
                output += f"• {rel_path}: {size_mb:.2f} MB\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error analyzing file system: {str(e)}" 