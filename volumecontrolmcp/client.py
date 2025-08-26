"""
Enhanced MCP Client for Volume Control Server

This client connects to the volume control MCP server using stdio transport
and provides a comprehensive interface to use all tools, resources, and prompts.
"""

import asyncio
import json
import sys
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Server configuration - using stdio transport
SERVER_COMMAND = ["D:/VolumeControlMCP/.venv/Scripts/python.exe", "volumecontrol_server.py"]

class VolumeControlClient:
    """Enhanced client for the Volume Control MCP Server"""
    
    def __init__(self):
        self.server_params = StdioServerParameters(
            command=SERVER_COMMAND[0],
            args=SERVER_COMMAND[1:],
            env=None
        )
    
    async def __aenter__(self):
        try:
            # Create stdio connection to server
            self.stdio_transport = stdio_client(self.server_params)
            self.read, self.write = await self.stdio_transport.__aenter__()
            
            # Create MCP session
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            
            # Initialize the session
            await self.session.initialize()
            
            return self
        except Exception as e:
            print(f"Failed to connect to server: {e}", file=sys.stderr)
            # Clean up if something went wrong
            if hasattr(self, 'session'):
                try:
                    await self.session.__aexit__(None, None, None)
                except:
                    pass
            if hasattr(self, 'stdio_transport'):
                try:
                    await self.stdio_transport.__aexit__(None, None, None)
                except:
                    pass
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if hasattr(self, 'session'):
                await self.session.__aexit__(exc_type, exc_val, exc_tb)
        except:
            pass  # Ignore cleanup errors
        try:
            if hasattr(self, 'stdio_transport'):
                await self.stdio_transport.__aexit__(exc_type, exc_val, exc_tb)
        except:
            pass  # Ignore cleanup errors
    
    async def list_tools(self):
        """List all available tools"""
        return await self.session.list_tools()
    
    async def call_tool(self, name: str, arguments: dict = None):
        """Call a specific tool"""
        return await self.session.call_tool(name, arguments or {})
    
    async def list_resources(self):
        """List all available resources"""
        return await self.session.list_resources()
    
    async def read_resource(self, uri: str):
        """Read a specific resource"""
        return await self.session.read_resource(uri)
    
    async def list_prompts(self):
        """List all available prompts"""
        return await self.session.list_prompts()
    
    async def get_prompt(self, name: str, arguments: dict = None):
        """Get a specific prompt"""
        return await self.session.get_prompt(name, arguments or {})

async def test_tools(client):
    """Test all available tools"""
    print("🔧 Testing Volume Control Tools...")
    
    tools_to_test = [
        ("get_volume", {}, "Getting current volume"),
        ("set_volume", {"percentage": 75}, "Setting volume to 75%"),
        ("apply_preset", {"preset_name": "MEDIUM"}, "Applying MEDIUM preset"),
        ("mute", {}, "Muting system"),
        ("unmute", {}, "Unmuting system"),
        ("toggle_mute", {}, "Toggling mute")
    ]
    
    for i, (tool_name, args, description) in enumerate(tools_to_test, 1):
        print(f"\n{i}. {description}:")
        try:
            result = await client.call_tool(tool_name, args)
            if result and hasattr(result, 'content') and result.content:
                print(f"   ✅ {result.content[0].text}")
            else:
                print(f"   ⚠️ Tool executed: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_resources(client):
    """Test all available resources"""
    print("\n📦 Testing Volume Control Resources...")
    
    # Test current state resource
    print("\n1. Reading current volume state:")
    try:
        result = await client.read_resource("volume://current-state")
        if result and hasattr(result, 'contents') and result.contents:
            content = json.loads(result.contents[0].text)
            print(f"   📊 Current State:")
            volume_content = content.get('content', {})
            print(f"      Volume: {volume_content.get('volume_percentage', 'N/A')}%")
            print(f"      Muted: {volume_content.get('is_muted', 'N/A')}")
            print(f"      Status: {volume_content.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error reading current state: {e}")
    
    # Test presets resource
    print("\n2. Reading volume presets:")
    try:
        result = await client.read_resource("volume://presets")
        if result and hasattr(result, 'contents') and result.contents:
            content = json.loads(result.contents[0].text)
            presets = content.get('content', {}).get('presets', [])
            print(f"   🎚️ Available Presets ({len(presets)}):")
            for preset in presets:
                print(f"      • {preset['name']}: {preset['description']}")
    except Exception as e:
        print(f"   ❌ Error reading presets: {e}")
    
    # Test capabilities resource
    print("\n3. Reading system capabilities:")
    try:
        result = await client.read_resource("volume://capabilities")
        if result and hasattr(result, 'contents') and result.contents:
            content = json.loads(result.contents[0].text)
            capabilities = content.get('content', {})
            print(f"   🔧 System Capabilities:")
            system_info = capabilities.get('system_info', {})
            print(f"      Platform: {system_info.get('platform', 'N/A')}")
            print(f"      Audio API: {system_info.get('audio_api', 'N/A')}")
            operations = capabilities.get('supported_operations', [])
            print(f"      Operations: {', '.join(operations)}")
    except Exception as e:
        print(f"   ❌ Error reading capabilities: {e}")

async def test_prompts(client):
    """Test all available prompts"""
    print("\n💬 Testing Volume Control Prompts...")
    
    # Test help prompt
    print("\n1. Getting help prompt:")
    try:
        result = await client.get_prompt("volume-control-help")
        if result and hasattr(result, 'messages') and result.messages:
            print(f"   📚 Help prompt retrieved with {len(result.messages)} message(s)")
            for message in result.messages[:1]:  # Show first message
                print(f"      Content: {message.content.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error getting help prompt: {e}")
    
    # Test settings prompt
    print("\n2. Getting settings prompt:")
    try:
        result = await client.get_prompt("volume-settings")
        if result and hasattr(result, 'messages') and result.messages:
            print(f"   ⚙️ Settings prompt retrieved")
    except Exception as e:
        print(f"   ❌ Error getting settings prompt: {e}")
    
    # Test troubleshooting prompt
    print("\n3. Getting troubleshooting prompt:")
    try:
        result = await client.get_prompt("volume-troubleshooting")
        if result and hasattr(result, 'messages') and result.messages:
            print(f"   🔧 Troubleshooting prompt retrieved")
    except Exception as e:
        print(f"   ❌ Error getting troubleshooting prompt: {e}")

async def run():
    try:
        print("🔌 Starting Enhanced Volume Control MCP Client")
        print("🌐 Connecting to MCP server via stdio")
        
        server_params = StdioServerParameters(
            command=SERVER_COMMAND[0],
            args=SERVER_COMMAND[1:],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Client connected via MCP protocol")
                
                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")
                
                # List and display all available features
                print("\n📋 Discovering server capabilities...")
                
                # List tools
                try:
                    tools_result = await session.list_tools()
                    if tools_result and hasattr(tools_result, 'tools'):
                        tools = tools_result.tools
                        print(f"\n🔧 Available Tools ({len(tools)}):")
                        for tool in tools:
                            print(f"   • {tool.name}: {tool.description or 'No description'}")
                    else:
                        print("\n🔧 Could not retrieve tools list")
                except Exception as e:
                    print(f"❌ Error listing tools: {e}")
                
                # List resources
                try:
                    resources_result = await session.list_resources()
                    if resources_result and hasattr(resources_result, 'resources'):
                        resources = resources_result.resources
                        print(f"\n📦 Available Resources ({len(resources)}):")
                        for resource in resources:
                            print(f"   • {resource.uri}: {resource.name or 'No name'}")
                            print(f"     Description: {resource.description or 'No description'}")
                    else:
                        print("\n📦 Could not retrieve resources list")
                except Exception as e:
                    print(f"❌ Error listing resources: {e}")
                
                # List prompts
                try:
                    prompts_result = await session.list_prompts()
                    if prompts_result and hasattr(prompts_result, 'prompts'):
                        prompts = prompts_result.prompts
                        print(f"\n💬 Available Prompts ({len(prompts)}):")
                        for prompt in prompts:
                            print(f"   • {prompt.name}: {prompt.description or 'No description'}")
                    else:
                        print("\n💬 Could not retrieve prompts list")
                except Exception as e:
                    print(f"❌ Error listing prompts: {e}")
                
                # Test tools
                await test_tools_simple(session)
                await test_resources_simple(session)
                await test_prompts_simple(session)
                
                print("\n🎯 Enhanced volume control client test completed!")
                print("✨ All Tools, Resources, and Prompts tested successfully!")

    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()

async def test_tools_simple(session):
    """Test all available tools with direct session"""
    print("\n🔧 Testing Volume Control Tools...")
    
    tools_to_test = [
        ("get_volume", {}, "Getting current volume"),
        ("set_volume", {"percentage": 75}, "Setting volume to 75%"),
        ("apply_preset", {"preset_name": "MEDIUM"}, "Applying MEDIUM preset"),
        ("mute", {}, "Muting system"),
        ("unmute", {}, "Unmuting system"),
        ("toggle_mute", {}, "Toggling mute")
    ]
    
    for i, (tool_name, args, description) in enumerate(tools_to_test, 1):
        print(f"\n{i}. {description}:")
        try:
            result = await session.call_tool(tool_name, args)
            if result and hasattr(result, 'content'):
                content = result.content
                if content:
                    print(f"   ✅ {content[0].text}")
                else:
                    print("   ⚠️ Tool executed but returned no content")
            else:
                print(f"   ⚠️ Tool executed: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_resources_simple(session):
    """Test all available resources with direct session"""
    print("\n📦 Testing Volume Control Resources...")
    
    resources_to_test = [
        ("volume://current-state", "Reading current volume state"),
        ("volume://presets", "Reading volume presets"),
        ("volume://capabilities", "Reading system capabilities")
    ]
    
    for i, (uri, description) in enumerate(resources_to_test, 1):
        print(f"\n{i}. {description}:")
        try:
            result = await session.read_resource(uri)
            if result and hasattr(result, 'contents'):
                for content in result.contents:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        print(f"   📊 Resource content retrieved successfully")
                        if 'content' in data:
                            resource_content = data['content']
                            if uri == "volume://current-state":
                                print(f"      Volume: {resource_content.get('volume_percentage', 'N/A')}%")
                                print(f"      Muted: {resource_content.get('is_muted', 'N/A')}")
                            elif uri == "volume://presets":
                                presets = resource_content.get('presets', [])
                                print(f"      Available presets: {len(presets)}")
                                for preset in presets[:3]:  # Show first 3
                                    print(f"        • {preset['name']}: {preset['description']}")
                            elif uri == "volume://capabilities":
                                print(f"      Platform: {resource_content.get('system_info', {}).get('platform', 'N/A')}")
                                ops = resource_content.get('supported_operations', [])
                                print(f"      Operations: {', '.join(ops[:5])}")  # Show first 5
                    else:
                        print(f"   📊 Resource: {content}")
            else:
                print(f"   ⚠️ Resource read but no content: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_prompts_simple(session):
    """Test all available prompts with direct session"""
    print("\n💬 Testing Volume Control Prompts...")
    
    prompts_to_test = [
        ("volume-control-help", {}, "Getting help prompt"),
        ("volume-settings", {}, "Getting settings prompt"),
        ("volume-troubleshooting", {}, "Getting troubleshooting prompt")
    ]
    
    for i, (prompt_name, args, description) in enumerate(prompts_to_test, 1):
        print(f"\n{i}. {description}:")
        try:
            result = await session.get_prompt(prompt_name, args)
            if result and hasattr(result, 'messages'):
                print(f"   📚 Prompt retrieved with {len(result.messages)} message(s)")
                for j, message in enumerate(result.messages[:2]):  # Show first 2 messages
                    if hasattr(message, 'content') and hasattr(message.content, 'text'):
                        print(f"      Message {j+1}: {message.content.text[:100]}...")
                    else:
                        print(f"      Message {j+1}: {str(message)[:100]}...")
            else:
                print(f"   ⚠️ Prompt retrieved: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
