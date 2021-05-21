
library(shiny)
library(tidyverse)
library(plot.matrix)
library(plotly)
library(RColorBrewer)

# Define UI for application that draws a histogram
ui <- fluidPage(

  fluidRow(
    column(2,
       radioButtons("R1", "ROI 1", choices = c("BA44","BA6","PFt"), selected = "BA44")      
    ),
    column(2,
       radioButtons("R2", "ROI 2", choices = c("BA44","BA6","PFt"), selected = "BA6")      
    ),
    column(2,
       radioButtons("R3", "ROI 3", choices = c("BA44","BA6","PFt"), selected = "PFt")      
    )
  ),
  
  fluidRow(
    column(3,
      plotOutput("R1_R2")
    ),
    column(3,
      plotOutput("R2_R3")
    )
  ),
  
  fluidRow(
    column(6,
       plotlyOutput("sankey")    
    )
  )
  

)

nbin=6

datadir <- paste0(getwd(),"/results_lorenzo")
filetemplate <- paste0(datadir,"/ISFC_Motion-Scrambled_SEED-TARGET_thr200_binNBIN.txt")

# Define server logic required to draw a histogram
server <- function(input, output) {

  observe({
  
    R1_R2_file <- str_replace_all(filetemplate, c("SEED"=input$R1, "TARGET"=input$R2, "NBIN"=nbin))
    R2_R3_file <- str_replace_all(filetemplate, c("SEED"=input$R2, "TARGET"=input$R3, "NBIN"=nbin))
    
    R1_R2 <- read.table(R1_R2_file, header = F, sep = " ") %>% as.matrix()
    R2_R3 <- read.table(R2_R3_file, header = F, sep = " ") %>% as.matrix()
    
    R1_names <- map(1:nbin, ~ paste0(input$R1,"_",.x))
    R2_names <- map(1:nbin, ~ paste0(input$R2,"_",.x))
    R3_names <- map(1:nbin, ~ paste0(input$R3,"_",.x))
    
    # R1_R2 names
    rownames(R1_R2) <- R1_names
    colnames(R1_R2) <- R2_names

    # R2_R3 names
    rownames(R2_R3) <- R2_names
    colnames(R2_R3) <- R3_names
    

    output$R1_R2 <- renderPlot(
      R1_R2 %>% plot(asp=T, digits=2, col=brewer.pal(9,"Reds"), key=NULL)
    )

    output$R2_R3 <- renderPlot(
      R2_R3 %>% plot(asp=T, digits=2, cex=0.5, col=brewer.pal(9,"Reds"), key=NULL)
    )

    
    zthr = 0
    
    # I need to add the nbin since the targets *in each matrix* are shifted of
    # nbin positions wrt to the source.
    # Note that target_R1_R2 = source_R2_R3.
    # I also subtract 1 since for the plot the node numba start at zero
    idx_R1_R2 <- which(R1_R2 > zthr, arr.ind = T)
    source_R1_R2 <- idx_R1_R2[,1] - 1
    target_R1_R2 <- idx_R1_R2[,2] - 1 + nbin
    vals_R1_R2 <- R1_R2[idx_R1_R2]
    
    idx_R2_R3 <- which(R2_R3 > zthr, arr.ind = T)
    source_R2_R3 <- idx_R2_R3[,1] - 1 + nbin 
    target_R2_R3 <- idx_R2_R3[,2] - 1 + nbin + nbin
    vals_R2_R3 <- R2_R3[idx_R2_R3]
    
    
    CC <- cbind(R1_R2, R2_R3)
    source <- c(source_R1_R2, source_R2_R3)
    target <- c(target_R1_R2, target_R2_R3)
    vals <- c(vals_R1_R2, vals_R2_R3)
    
    ## plot the sankey

    # Prepare color palettes
    # display.brewer.pal(5,"Greens")
    FANTASIA <- brewer.pal(nbin, "Paired")
    REDS <- colorRampPalette(c(brewer.pal(5,"Reds")[2],brewer.pal(5,"Reds")[5]))
    GREENS <- colorRampPalette(c(brewer.pal(5,"Greens")[2],brewer.pal(5,"Greens")[5]))
    BLUES <- colorRampPalette(c(brewer.pal(5,"Blues")[2],brewer.pal(5,"Blues")[5]))
    
    # prepare link_colors by generating a named character that will be used as a lookup
    # https://www.infoworld.com/article/3323006/do-more-with-r-quick-lookup-tables-using-named-vectors.html
    # link_colors_lookup <- brewer.pal(dim(CC)[1],"Reds")
    # link_colors_lookup <- REDS
    # names(link_colors_lookup) <- rownames(CC)
    # link_colors <- map_chr(names(source), ~ link_colors_lookup[.x] %>% unname() %>% toRGB(alpha = 0.3))
    
    x_pos <- c(rep(0,nbin),rep(1,nbin),rep(2,nbin))
    y_pos <- rep(seq(1:nbin),3)
    
    p <- plot_ly(
      type = "sankey",
      arrangement = "freedom", hoverinfo = "skip", 
      textfont = list(family = "Arial"),
      orientation = "h",
      node = list(
        label = c(R1_names, R2_names, R3_names),
        x = x_pos/max(x_pos),
        y = y_pos/max(y_pos),
        color = c(FANTASIA, GREENS(nbin), BLUES(nbin)),
        pad = 5,
        thickness = 20
      ),
      link = list(
        source = source,
        target = target,
        value = vals
        # color = link_colors
      )
    )
    
    output$sankey <- renderPlotly(p)
    
    
  })

}

# Run the application 
shinyApp(ui = ui, server = server)











