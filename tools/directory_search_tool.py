from typing import Optional, Type
from crewai.tools import tool
from pydantic import BaseModel, Field
import os
import glob
from pathlib import Path

class DirectorySearchToolSchema(BaseModel):
    """Input for DirectorySearchTool."""
    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the directory's content",
    )
    directory: str = Field(
        default=".",
        description="Directory you want to search (defaults to current directory)"
    )

class DirectorySearchTool:
    """A tool that can be used to search through directory contents semantically."""
    
    def __init__(self, directory: Optional[str] = None):
        self.directory = directory or "."
        self.supported_extensions = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
            '.md', '.txt', '.json', '.xml', '.yaml', '.yml', '.ini',
            '.cfg', '.conf', '.sh', '.bat', '.ps1', '.sql'
        ]
    
    def _get_files_in_directory(self, directory: str) -> list:
        """Get all supported files in the directory recursively."""
        files = []
        try:
            for ext in self.supported_extensions:
                pattern = os.path.join(directory, f"**/*{ext}")
                files.extend(glob.glob(pattern, recursive=True))
            return files
        except Exception as e:
            return [f"Error accessing directory: {str(e)}"]
    
    def _read_file_content(self, file_path: str) -> str:
        """Read file content safely."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def _search_in_content(self, content: str, query: str) -> bool:
        """Simple semantic search in content."""
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        # Check if all query terms are present in content
        return all(term in content_lower for term in query_terms)
    
    def search_directory(self, search_query: str, directory: str = None) -> str:
        """Search for content in directory files."""
        search_dir = directory or self.directory
        
        if not os.path.exists(search_dir):
            return f"❌ Directory '{search_dir}' does not exist"
        
        # Get all files in directory
        files = self._get_files_in_directory(search_dir)
        
        if not files:
            return f"❌ No supported files found in directory '{search_dir}'"
        
        # Search through files
        results = []
        query_terms = search_query.lower().split()
        
        for file_path in files:
            try:
                # Skip if it's a directory
                if os.path.isdir(file_path):
                    continue
                
                # Read file content
                content = self._read_file_content(file_path)
                
                # Check if query matches content
                if self._search_in_content(content, search_query):
                    # Get file stats
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024
                    
                    # Get relative path
                    rel_path = os.path.relpath(file_path, search_dir)
                    
                    # Extract relevant snippet (first 200 chars)
                    snippet = content[:200].replace('\n', ' ').strip()
                    if len(content) > 200:
                        snippet += "..."
                    
                    results.append({
                        'file': rel_path,
                        'size_kb': round(file_size_kb, 2),
                        'snippet': snippet
                    })
                    
                    # Limit results to avoid overwhelming output
                    if len(results) >= 10:
                        break
                        
            except Exception as e:
                continue
        
        if not results:
            return f"❌ No files found matching query '{search_query}' in directory '{search_dir}'"
        
        # Format results
        output = f"🔍 **DIRECTORY SEARCH RESULTS**\n"
        output += f"Query: '{search_query}'\n"
        output += f"Directory: '{search_dir}'\n"
        output += f"Found: {len(results)} matching files\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"**{i}. {result['file']}** ({result['size_kb']} KB)\n"
            output += f"```\n{result['snippet']}\n```\n\n"
        
        return output

# Global instance
directory_search_tool = DirectorySearchTool()

@tool("Directory Search Tool")
def search_directory_content(search_query: str, directory: str = ".") -> str:
    """
    Search through directory contents semantically to find relevant files and code.
    
    This tool is particularly useful for:
    - Finding specific functions or classes in codebases
    - Locating configuration files
    - Searching for specific patterns or keywords
    - Understanding project structure
    - Finding relevant code examples
    
    Parameters:
        search_query (str): The search query to look for in files
        directory (str): Directory to search (defaults to current directory)
    
    Returns:
        str: Formatted search results with file paths and content snippets
    """
    return directory_search_tool.search_directory(search_query, directory)

@tool("Codebase Analysis Tool")
def analyze_codebase_structure(directory: str = ".") -> str:
    """
    Analyze the structure of a codebase to understand its organization.
    
    Parameters:
        directory (str): Directory to analyze (defaults to current directory)
    
    Returns:
        str: Codebase structure analysis with file types and organization
    """
    if not os.path.exists(directory):
        return f"❌ Directory '{directory}' does not exist"
    
    try:
        # Get all files and directories
        all_files = []
        all_dirs = []
        
        for root, dirs, files in os.walk(directory):
            # Get relative paths
            rel_root = os.path.relpath(root, directory)
            
            for file in files:
                file_path = os.path.join(rel_root, file)
                all_files.append(file_path)
            
            for dir_name in dirs:
                dir_path = os.path.join(rel_root, dir_name)
                all_dirs.append(dir_path)
        
        # Analyze file types
        file_types = {}
        for file in all_files:
            ext = os.path.splitext(file)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Generate report
        output = f"📁 **CODEBASE STRUCTURE ANALYSIS**\n"
        output += f"Directory: '{directory}'\n\n"
        
        output += f"📊 **STATISTICS:**\n"
        output += f"• Total Files: {len(all_files)}\n"
        output += f"• Total Directories: {len(all_dirs)}\n"
        output += f"• File Types: {len(file_types)}\n\n"
        
        if file_types:
            output += f"📄 **FILE TYPES:**\n"
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:10]:  # Top 10
                output += f"• {ext or 'no extension'}: {count} files\n"
            output += "\n"
        
        # Show directory structure (top level)
        output += f"📂 **DIRECTORY STRUCTURE:**\n"
        top_level_dirs = [d for d in all_dirs if '/' not in d and '\\' not in d]
        for dir_name in sorted(top_level_dirs):
            output += f"• {dir_name}/\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error analyzing codebase: {str(e)}"

@tool("File Content Reader")
def read_file_content(file_path: str, max_lines: int = 50) -> str:
    """
    Read and display the content of a specific file.
    
    Parameters:
        file_path (str): Path to the file to read
        max_lines (int): Maximum number of lines to display (default: 50)
    
    Returns:
        str: File content with line numbers
    """
    if not os.path.exists(file_path):
        return f"❌ File '{file_path}' does not exist"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if not lines:
            return f"📄 File '{file_path}' is empty"
        
        # Limit lines
        display_lines = lines[:max_lines]
        total_lines = len(lines)
        
        output = f"📄 **FILE CONTENT: {file_path}**\n"
        output += f"Total lines: {total_lines}\n"
        if total_lines > max_lines:
            output += f"Showing first {max_lines} lines\n"
        output += f"{'='*60}\n\n"
        
        for i, line in enumerate(display_lines, 1):
            output += f"{i:3d}: {line.rstrip()}\n"
        
        if total_lines > max_lines:
            output += f"\n... (showing {max_lines} of {total_lines} lines)\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error reading file '{file_path}': {str(e)}" 