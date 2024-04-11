### Ticket Types
There are several ticket types to track the work of a project.

#### Epics

An Epic is a body of work that can be break down into multiple user stories (issues). Epics are too much work for one sprint. An epic is almost always delivered over a set of sprints.

#### Issues

The team use issues to track individual pieces of work that must be completed. An issue represents a story (Scrum), a bug or a task. Typically, issues represent things like big features, user requirements and software bugs.

The work for an issue must be small enough such that it can done in one sprint.

#### Sub-Tasks

Issues can have sub-tasks that are assigned and tracked individually. There are following reasons for creating a sub-tasks:

- Splitting an issue into even smaller chunks
- Allowing various aspects of an issue to be assigned to different people
- Creating a to-do list for an issue

#### Customised Types

Each issue type can be customise. Additional, you can add your own issue type. For example:

- Bug
- Documentation

Only users with admin permission can customise issue types. This feature is available on the project settings menu.

## Features of an issue

### Estimation

The estimation of an issue can be tracked the velocity of a project.
Estimating issues in the backlog helps to predict how long portions of the backlog might take to be delivered.
The most popular estimation scheme is story points.
Story points measure the complexity of one issue relative to the others.
The estimation of a issue can be stored in the "Estimate" field.

### Flag
Flagging an issue can be useful for:

- indicating that the assignee of the ticket can not finish his work because of having too little time. Other team members are welcome to take over.
- marking an issue as blocked, for example by other not done issues or another team.

### Priority

Issues can have priorities. That allows you to rank your issues and what you should work on next.

### Time Tracking

There is a time tracking possible on each issue.
So, you can track the time you spend working on the ticket.
To start and stop the time tracking, you can simply click on the time tracking button.
Breaks are supported and it shows what time you already spent for this issue.
Time tracking means hard discipline.
Every time when you do a break, you need to click on the time tracking button of the issue and click again when you re-start working.

### Labels

Labels are tags or keywords that can be added to issues.
They let you categorise an issue.
It is similar to the hashtag ( # ) used in twitter.
They also can used for searching an issue.

### Fix version

The fix version of an issue identifies the version when a issue should be done.

### Links in issues

Issues can be linked to keep track of duplicate or related work. If you want to create a link of another issue in your issue:

1. open the issue and and click on link issue
2. choose the reason why you want to link the issue (for example: 'duplicates')
3. choose the issue that you want to link

You can also link confluence pages or a web-site to an issue.

### Attachment

Attachments can be added to an issue. You can add folders, text files, PDFs, images, etc.

### Sprint

The sprint field of an issue identifies the sprint in that the issue should be processed.

### Status

Each issue has an status field that specify the current status of an issue - for example:

- `TO DO`
- `In progress`
- `Review`
- `Approved`
- `Done`


## Users Types

### Reporter

The reporter is the person who raised the request. Usually, this is the same person who created the issue, but not always - for example: you can create issues on behalf of someone else.

### Assignee

The assignee is the person who is responsible for completing the issue, including sub-tasks. The assignee is working on the issue. An issue with sub-tasks can assigned to multiple persons. The person of the parent issue is the most responsible person (like a kind of lead).

### Watcher

A watcher is a person that has at least read permissions on the project and keep an eye on the project.

It is possible to watching an issue that allows persons to keep an eye on a special issue. The watcher will be informed whenever there is any update or changes in that issue.

#### Start watching a issue

1. Go to the issue
2. Click on the eye symbol on the top right
3. Click on Add watchers and add the new watcher

#### Stop watching a issue

1. Go to the issue
1. Click on the eye symbol on the top right
1. Hover over the name of the watcher you want to remove
1. Click on the X

## Work with issues

### Sprints

A sprint - also known as an iteration - is a short, well defined time-boxed period when work of a set amount of work should be completed. The most often chosen time period for a sprint is two weeks or one month

In Jira, you view sprints on a board and assign issues to the sprints. Each individual issue as a sprint field for seeing the sprint that the issue is part of.

### Backlog

The backlog is a list of tasks that represents the outstanding work in a project. Any issues of the backlog can be add to a sprint.

If you raise an issue, you should put it into the backlog. The team decides when it will be put into the sprint

### Board

The board displays all issues of the project that are in the current sprint. It gives you an overview:

- who is working on which issue
- the status of each individual issue
- the assignee of each issue
- if issues are blocked or not

## Roadmap

A good product road map makes sure that everyone working on the product understands the status of work and are aligned on upcoming priorities. Road maps in Jira enable you to quickly create a timeline of your plans, update your priorities and communicate the status of the work.

### Releases

A release present a point in time of your project. Releases can be used to schedule how features are rolled out or as a way to organise work that has been completed for the project.

Jira provides a releases feature. You can add releases to each issue to specify which version contains which feature. The releases page shows how much work has been completed in each release version.

### Reports

There are several plugins that can be used to create a report of the current project status. The most important is the Sprint burn down chart.

#### Sprint burn down chart

- The burn down chart shows the amount of work remaining on a sprint. The following will help you to understand the burn down chart in Jira:
- The burn down chart in Jira is board-specific.
- The vertical axis represents the estimation statistic that you have configured - for example issue count or story points.
- The burn down chart is based on the board’s column mapping. Only issues with status Done (left-most column) will be considered.
- The grey guideline represent the optimal sprint burn down.

## Plugins

Jira provides several plugins that can be activated.

### Code

You can connect your Github for the project with the Jira project. In our system, this plugin will be fully configured in the near future.

### Confluence

You can link a confluence space to your Jira project. You can see, add, remove and edit each page in the space using the Jira software.
