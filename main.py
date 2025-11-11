from src.app import root_agent

def main():
    print("Hello from swarm!")

    result = root_agent.run("Go to https://www.google.com and search for 'AI engineer code summit NYC'")
    print(result)

if __name__ == "__main__":
    main()
