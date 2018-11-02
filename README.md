# apply_first

## Background

    I’m currently applying to jobs, and I’ve gotten back some messages
    like to the effect of, ‘we’ve’ filled this position etc. To remedy
    the problem and avoid applying to stale jobs that aren’t available
    anymore, I want to be the first person to apply to a job opening.

    This started out as a simple script using requests to make get
    requests to career pages, and using lxml and an XPath found using
    https://github.com/trembacz/xpath-finder. I quickly found that this
    was a bad tactic to scrape, as a lot more sites than I’d expected
    use dynamically created careers pages.

    I then converted it to use selenium and geckodriver (firefox) which
    gave a lot more consistent results. Basically, it takes in a list of
    companies, their name, job-board url, and XpPth to engineering careers. 

    The response is then parsed out using lxml, and checked against the
    current entries in the SQLite3 DB. Old career postings are pruned,
    and new ones are added to the DB, as well as emailed to the user via
    Sentry.io’s SDK.

    I was going to set this up as a cron job, but gecko does not play
    well on headless systems. So, I converted the script to an actual
    Flask app, using apscheduler to run a job every 15 minutes, and
    changed from using geckodriver to chromedriver.

    I then decided to dockerize the app for deployment.

### Instruction to create a Docker image

    Clone the repo.

    Create flask app project in Sentry.io(you must signup first).  

    Copy the sentry sdk key into the Dockerfile
    
    Build the image, and deploy.

