# Feature Flag Research

I'm tracking this file to compare the various solutions that I've tried out. I started in README.md, but Big Pickle went and overwrote it :(.

# Client System

I've just refactored this to work with OpenFeature, an open source SDK that is compatible with many feature flagging systems. The thought here is that we write once in our code using OpenFeature, then we can migrate backends to our heart's desire. Of course this never ends up happening, but I think by stating we are going to use OpenFeature, that limits friction and lets us get started sooner.

https://openfeature.dev/

# Feature Flagging Systems

I messed around with a number of systems in my exploration. The following is an overview of what I experienced.

## AWS AppConfig

https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html

This is the first one I tried. I really liked it to start with, but as I started using other solutions, the luster wore off some. It is very good at many things, but it seems that you have to build quite a lot around it to design your "system." 

The setup was very straightforward (for an AWS service, anyway). You create an "Application," then you create "Environments." You then create a Configuration Profile which is where your flags exist. Flags can either be simple boolean flags or they can be more complex configuration structures. I recommend we stick with simple flags as the complex structures might encourage us to put things in here that are not feature flag related - we should keep a strict boundary about what is configured in this system and what is not.

Once you have your Configuration Profile, you then create "versions" of it. Those versions are deployed to environments using a Deployment Strategy. Deployment Strategies can range from just deploying outright to slowly ramping up the traffic that gets the new configuration. So if you enable a feature in a version that you then deploy to "US Production," that version will only be served to a percentage of traffic. It also has the ability to roll back the configuration if it detects issues by way of CloudWatch errors.

All in all, this satisfies Item 1 in our Technology Decision Making Rubric - if Amazon provides something, use it. We need to do a deeper analysis on the features that we need before we can say that conclusively, but it remains a strong candidate.

### Pros
* AWS Managed - no need to procure or analyze new software
* Straight Forward - configuration is pretty easy to grok

### Cons
* AWS Silliness - regions and other strangenesses
* Costs are challenging to decipher - it could cost $5000-$10000 per year to run this, or it could be next to free. It's hard to get a good read on that.
* No native OpenFeature support for most of our languages.
* Have to build some things to make it super useful.

## Unleash

https://www.getunleash.io/

## Flipt

https://flipt.io/

* Uses Git as a backend.
* Is OpenSource largely. Pro version unlocks some GitOps features and integrations.
* Not terribly pricey, but have to run the infrastructure
* Never actually got it working - was not readily intuitive like Unleash or AppConfig

## FlagD

https://flagd.dev/

* Completely OpenSource
* Good OpenFeature support across all languages we use
* Must run the infra ourselves, not support.
* Community size?

# Comparison

## Cost

For the purpose of this exercise, I priced out what it might cost if we hit whatever service we used every 30 seconds in 6 environments.

| Solution | License Model | Predicted Cost | Notes |
| ---- | ---- | ---- | ---- |
| AppConfig | Per Call | $5000 or Less | It might be far less than this, or double. Need more research |
| Unleash | $75/seat/month | $9000 | 10 seats for full year. May be able to do open source |
| Flipt | $200/month for Pro | $2400 | Can run Open Source but some features limited. Have to figure infrastructure and people costs. |
| FlagD | Open Source | $0 | Must run the infrastructure and no support. |

## Features

| Feature | AppConfig | Unleash | Flipt | FlagD |
| ---- | ---- | ---- | ---- | ---- |
| Simple Flags | ✔︎ | ✔︎ | ✔︎ | ✔︎ |
| Freeform Config | ✔︎ | ⨯ | ? | ? |
| Auto Rolllback on Errors | ✔︎ | ? | ? | ? |

# Recommendation

This is in progress, but my recommendation is for us to use OpenFeature on the "client" side and to spin up a simple FlagD server on Amazon and use that to start with. I think we should continue to evaluate commercial versions. So far I have liked Unleash quite a lot, but the licensing is a little strange given it is per seat, so we would have to have a solid plan for how we are going to use it for our whole process before committing to it.

With a combination of OpenFeature and FlagD, this will get us started actually doing the act of feature flagging, which will push us to experience what we really like and need from a system. By working out of the gate with OpenFeature, we shouldn't have to change a lot of "client" side code should we ultimately decide to pay somebody to run our feature flags for us.
