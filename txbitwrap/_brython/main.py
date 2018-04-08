""" main app entrypoint """
import terminal

def main(cfg, ctx):

    def on_event(_, event):
        console.log('__EVENT__', event)

        # FIXME this should receive events from upstream
        #ctx.ctl.on_event(event)

    ctx.bind(schema='octoe', callback=on_event)

terminal.__onload(callback=main)
