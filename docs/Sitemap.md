This diagram maps out the various endpoints on the site, including webpages as well as API endpoints in the future. Subgraph names are to be ignored.

```mermaid
graph TD
    root["/"]
    subgraph sg_root
        api
        accounts
        dashboard
    end
    
    root --> api
    root --> accounts
    root --> dashboard

    subgraph sg_accounts
        direction LR
        signup
        login
        auth
        logout
        reset_password
        delete
        settings
    end

    accounts --> signup
    accounts --> login
    accounts --> auth
    accounts --> logout
    accounts --> reset_password
    accounts --> delete
    accounts --> settings

    subgraph sg_dashboard
        dashboard --> transactions
        dashboard --> categories
        dashboard --> reports
        dashboard --> goals
    end
```
