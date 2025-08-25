"""
MCP Client for Volume Control Server

This client connects to the volume control MCP server and provides
a simple interface to use all volume control tools.
"""

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import traceback

# Server parameters for volume control server
server_params = StdioServerParameters(
    command="python",
    args=["volume_control_server.py"],
)

async def run():
    try:
        print("🔌 Starting Volume Control MCP Client")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Session started")
                await session.initialize()
                
                print("🔧 Listing available tools...")
                tools = await session.list_tools()
                print(f"� Available tools ({len(tools.tools)}):")
                for tool in tools.tools:
                    print(f"  • {tool.name} - {tool.description}")
                
                print("\n🎮 Testing volume control tools...")
                
                # Test get_volume
                print("\n1. Getting current volume:")
                result = await session.call_tool("get_volume", arguments={})
                if result.content:
                    print(f"   � {result.content[0].text}")
                
                # Test set_volume
                print("\n2. Setting volume to 60%:")
                result = await session.call_tool("set_volume", arguments={"percentage": 60})
                if result.content:
                    print(f"   🔊 {result.content[0].text}")
                
                # Test get_volume again
                print("\n3. Checking volume after change:")
                result = await session.call_tool("get_volume", arguments={})
                if result.content:
                    print(f"   📊 {result.content[0].text}")
                
                # Test mute
                print("\n4. Muting system:")
                result = await session.call_tool("mute", arguments={})
                if result.content:
                    print(f"   🔇 {result.content[0].text}")
                
                # Test unmute
                print("\n5. Unmuting system:")
                result = await session.call_tool("unmute", arguments={})
                if result.content:
                    print(f"   🔊 {result.content[0].text}")
                
                # Test toggle_mute
                print("\n6. Toggling mute:")
                result = await session.call_tool("toggle_mute", arguments={})
                if result.content:
                    print(f"   🔄 {result.content[0].text}")
                
                print("\n🎯 Volume control test completed!")

    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
