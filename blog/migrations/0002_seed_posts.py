from django.db import migrations


SEED_POSTS = [
    {
        "slug": "kubernetes-on-a-raspberry-pi-cluster",
        "title": "Kubernetes on a Raspberry Pi cluster",
        "excerpt": "Why I built a 4-node k3s cluster on Pis, what broke, and the surprisingly useful workloads I actually run on it.",
        "content": (
            "Four Raspberry Pi 4s, a switch, and a weekend — that's what it took to get k3s humming on my desk.\n\n"
            "The interesting part wasn't the install. It was discovering that 'edge Kubernetes' isn't a marketing term; it's "
            "a real constraint set. ARM images, ephemeral storage, flaky power, no in-cluster load balancer — every decision "
            "has a small but real cost.\n\n"
            "I run three things on it now: a self-hosted Gitea, a Prometheus + Grafana stack scraped over Tailscale, and a "
            "nightly cron that backs up my photos to a Wasabi bucket. Total power draw is under 18W.\n\n"
            "If you're considering it, skip the Helm complexity for the first month. Plain manifests will teach you more "
            "than any chart ever will."
        ),
        "tags": ["Kubernetes", "Homelab", "Linux"],
    },
    {
        "slug": "the-cost-of-cold-starts-on-aws-lambda",
        "title": "The real cost of cold starts on AWS Lambda",
        "excerpt": "Provisioned concurrency, SnapStart, and the trade-offs nobody puts in the marketing slides.",
        "content": (
            "Cold starts are the boogeyman of serverless. Most of the advice you'll read online is half-right because it "
            "ignores the shape of your workload.\n\n"
            "I instrumented three production functions for a month — one bursty, one steady, one nightly batch — and the "
            "answer was different for each. Provisioned concurrency paid off only for the bursty one. SnapStart (Java) cut "
            "p99 by 70% but introduced a different class of bug: stale connection pools.\n\n"
            "The under-discussed cost isn't latency; it's the operational tax of having two execution modes. If you commit "
            "to provisioned concurrency, treat it like a fleet — alarms, autoscaling, the whole thing.\n\n"
            "Numbers, dashboards, and a decision tree in the post."
        ),
        "tags": ["AWS", "Serverless", "Performance"],
    },
    {
        "slug": "why-postgres-is-eating-my-redis-cache",
        "title": "Why Postgres is eating my Redis cache",
        "excerpt": "Unlogged tables, LISTEN/NOTIFY, and a quiet realization that I had too many moving parts.",
        "content": (
            "I deleted Redis from a side project last month and the service got faster. Not because Postgres is faster than "
            "Redis — it isn't — but because the round trip through 'two consistency models' was costing more than the cache "
            "saved.\n\n"
            "What replaced it: an UNLOGGED Postgres table for the hot data, LISTEN/NOTIFY for pub/sub, and a partial index "
            "tuned to the query I actually run.\n\n"
            "This isn't a 'Redis is bad' post. Redis is great at being Redis. It's a post about the hidden cost of running "
            "a second database when the first one already does 80% of what you need at 0% additional ops overhead.\n\n"
            "Benchmarks and the schema inside."
        ),
        "tags": ["Postgres", "Architecture", "Databases"],
    },
    {
        "slug": "a-developers-guide-to-self-hosting-in-2026",
        "title": "A developer's guide to self-hosting in 2026",
        "excerpt": "The 2026 stack: Tailscale, Caddy, Docker Compose, and the boring tools that quietly won.",
        "content": (
            "Self-hosting used to require a static IP, a reverse-proxy rabbit hole, and a Sunday afternoon. In 2026, the "
            "stack has settled and it's almost boring — which is the highest compliment you can give infrastructure.\n\n"
            "My current setup: a $5/mo VPS for the public endpoints, a NUC at home doing the heavy lifting, and Tailscale "
            "stitching them together. Caddy handles TLS without me thinking about it. Docker Compose is still the unsung hero.\n\n"
            "What I'm hosting: Linkding (bookmarks), Miniflux (RSS), a private Listmonk (newsletter), and this blog. Total "
            "monthly cost: under $7. Total ops time: maybe an hour a month, mostly upgrading containers.\n\n"
            "Inside: the compose files, the Tailscale ACLs, and the one mistake that almost cost me my data."
        ),
        "tags": ["Self-hosting", "DevOps", "Homelab"],
    },
]


def seed_posts(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    Tag = apps.get_model("blog", "Tag")

    for data in SEED_POSTS:
        if Post.objects.filter(slug=data["slug"]).exists():
            continue
        post = Post.objects.create(
            slug=data["slug"],
            title=data["title"],
            excerpt=data["excerpt"],
            content=data["content"],
        )
        for caption in data["tags"]:
            tag, _ = Tag.objects.get_or_create(caption=caption)
            post.tags.add(tag)


def remove_seed_posts(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    Post.objects.filter(slug__in=[p["slug"] for p in SEED_POSTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_posts, remove_seed_posts),
    ]
