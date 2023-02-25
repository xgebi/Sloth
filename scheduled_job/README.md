# Scheduled Job

Scheduled job is a small application which checks if there are scheduled posts ready to be published. If there are any, it'll pass them to post generation.

```
* * * * * <path-to-sloth>/scheduled_job/target/release/scheduled_job
```