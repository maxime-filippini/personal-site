# Cut over without an old-stack standby

After the verified Worker takes the custom domain, the FastAPI service will be decommissioned immediately rather than retained as a live rollback target. Recovery will use a previous Worker version when possible or proceed by fixing forward; Git history preserves the former implementation but not an operating standby. The legacy R2 bucket may remain temporarily as passive migration evidence and will not be read by the new production application.
