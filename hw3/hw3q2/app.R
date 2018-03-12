library(shiny)
library(ggplot2)
library(dplyr)

cdc <- read.csv("cleaned-cdc-mortality-1999-2010-2.csv")

ui <- fluidPage(
  tags$style("input[type='radio']{   
              margin: -6px;
             }"),
  titlePanel("Mortality Rates Time Series by State"),
  sidebarLayout(
    sidebarPanel(uiOutput("causeOutput"),
                 uiOutput("stateOutput"),
                 paste0("This visualization shows mortality rates (by cause) over available time period (1999-2010). ",
                        "Each state is shown individually along with national average (black line). ",
                        "Additionally, you can select a state for closer comparison against national average. ",
                        "For large comparison plot, values are shifted with mean centered at zero.")
    ),
    mainPanel(plotOutput("stateplot"),
              br(),br(),
              plotOutput("smplot")
    )
  )
)

server <- function(input, output) {
  output$causeOutput <- renderUI({
    selectInput("causeInput", "Cause",
                sort(unique(cdc$ICD.Chapter)),
                selected = "Neoplasms")
  })
  output$stateOutput <- renderUI({
    selectInput("stateInput", "State",
                sort(unique(cdc$State)),
                selected = "NY")
  })
  cdc_filt <- reactive({
    if (is.null(input$causeInput)) {
      return(NULL)
    }  
    cdc %>%
      filter(ICD.Chapter == input$causeInput)
  })
  national_avg <- reactive({
    if (is.null(input$causeInput)) {
      return(NULL)
    }
    cdc_filt() %>% 
      group_by(Year) %>%
      summarize(totalDeath = sum(Deaths), totalPop = sum(Population)) %>%
      mutate(Rate = (100000*totalDeath)/totalPop)
  })
  state <- reactive({
    if (is.null(input$stateInput)) {
      return(NULL)
    }
    cdc_filt() %>% 
      filter(State == input$stateInput)
  })
  output$smplot <- renderPlot({
    if (is.null(cdc_filt())) {
      return()
    }
    ggplot() + 
      geom_line(data = cdc_filt(), aes(x = Year, y = Crude.Rate, color = State)) +
      geom_line(data = national_avg(), aes(x = Year, y = Rate)) + 
      facet_wrap(~State, ncol = 7) + 
      labs(x = "", y = "") + ggtitle(input$causeInput) +
      theme(axis.text.x = element_text(angle=90),
            legend.position="none")
  }, height = 1200)
  output$stateplot <- renderPlot({
    if (is.null(cdc_filt())) {
      return()
    }
    
    national_mean <- mean(national_avg()$Rate)
    state_mean <- mean(state()$Crude.Rate)
    diff <- national_mean - state_mean
    
    ggplot() + 
      geom_line(data = state(), aes(x = Year, y = Crude.Rate+diff-national_mean), color = "blue", size = 1) +
      geom_line(data = national_avg(), aes(x = Year, y = Rate-national_mean), size = 1) + 
      geom_hline(yintercept = 0, linetype = "dotted") + 
      labs(x = "", y = "") + ggtitle(paste("National Average vs.", input$stateInput, "/", input$causeInput, "(centered at mean rate)"))
  })
}
shinyApp(ui = ui, server = server)
