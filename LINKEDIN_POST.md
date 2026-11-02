Safe to Send · Ep 01 — Your AI agent is three calls away from a full-table DELETE

AI agents can now reach Adobe Campaign Classic. Every permission you give one has a good reason. Almost nobody adds them up.

So I built a small tool that does. Give it an agent's grants and the controls you run, and it lists every dangerous outcome the agent can reach, and how many calls away it is.

The Black Friday helper agent I configured "sensibly" scored 100/100 exposure:
→ consent overwrite: 1 call
→ send with no unsubscribe link: 1 call
→ full-table DELETE: 2 calls
→ pausing the GDPR purge: 2 calls

Same agent, same permissions, behind a gate: 0/100. Every outcome stopped, and the control that stops it named.

This is Episode 01 of Safe to Send: 28 episodes on governing AI in CRM operations, each with its own open-source repo. Synthetic data only.

Run it on your own agent setup.

What would you never let an agent do in your CRM?

Repo: https://github.com/sghatge/safe-to-send-01-agent-blast-radius

#SafeToSend #AdobeCampaign #AIGovernance #MarketingOps
