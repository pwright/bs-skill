def plan(req):
    print("DEBUG: planner invoked", flush=True)
    # trivial planner: echo last message
    return req.messages[-1].content.strip()
