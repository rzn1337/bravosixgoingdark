from __future__ import annotations

from .base import Activity


class WatchVideo(Activity):
    """Open the browser to a YouTube search on the configured topics (GoHighLevel,
    CRM automation, n8n workflows, ...) and 'watch' — dwell for a while with the
    occasional scroll and small mouse move, like someone following a video."""

    name = "watch"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng
        watch = ctx.settings.watch
        urls = watch.urls or ["https://www.youtube.com"]
        url = rng.choice(urls)

        ctx.log.info("watch: opening browser at %s", url)
        proc = ctx.apps.launch_browser(url)
        if proc is not None:
            ctx.tracked.append(proc)

        if not ctx.exe.wait(rng.uniform(3.0, 6.0)):  # let the page load
            return
        ctx.focus.activate(ctx.apps.browser_title_hints())

        dwell = rng.uniform(watch.dwell_min_s, watch.dwell_max_s)
        ctx.log.info("watch: watching for ~%ds", int(dwell))
        w, h = ctx.screen_size
        remaining = dwell
        while remaining > 0 and not ctx.control.stopped():
            step = min(remaining, rng.uniform(6.0, 16.0))
            if not ctx.exe.wait(step):
                return
            remaining -= step
            roll = rng.random()
            if roll < 0.35:
                ctx.exe.scroll(rng.choice([-2, -1, 1, 2]))
            elif roll < 0.55:
                ctx.exe.move_to(
                    rng.randint(int(w * 0.2), int(w * 0.75)),
                    rng.randint(int(h * 0.2), int(h * 0.7)),
                )
