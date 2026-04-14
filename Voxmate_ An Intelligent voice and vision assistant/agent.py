"""
agent.py — FINAL STABLE VOXMATE
LiveKit + OpenAI (official)
Face Auth → Voice → Reasoning → Voice
"""

import os
import sys
import webbrowser
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation, openai

from prompts import AGENT_INSTRUCTION
from tools import (
    get_weather,
    search_web,
    send_email,
    open_youtube,
    open_instagram,
)
from face_auth_deepface import authenticate_face_deepface

load_dotenv()


class VoxmateAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=openai.LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
                open_youtube,
                open_instagram,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    print("🎧 Voxmate Agent starting...")

    session = AgentSession()
    await session.start(
        room=ctx.room,
        agent=VoxmateAssistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()
    print("✅ Voxmate is live and listening...")


if __name__ == "__main__":
    print("🚀 Launching Voxmate...\n")

    print("🔒 Face Authentication...\n")
    if not authenticate_face_deepface():
        print("❌ Face Authentication Failed.")
        sys.exit(1)

    print("✅ Face Authentication Successful!")

    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
