
library(parallel)
library(foreach)
library(doParallel)
recruitedCores <- detectCores() %/% 2
registerDoParallel(recruitedCores)

# function for the standard error
sderr <- function(x) sd(x)/sqrt(length(x))


atlastable <- function(Zcontrast, depth, datadir) {
  
  Zthrvol <- Zcontrast
  
  Zmask <- Zthrvol
  Zmask[Zmask !=0 ] = 1
  
  jubrain <- paste0(datadir,"/atlas_juelich_icbm.nii.gz") %>% readNIfTI()
  julabels <- paste0(datadir,"/labels_juelich.csv") %>% read.csv(.,stringsAsFactors=FALSE)
  julabels$index <- julabels$index + 1
  
  # I multiply a mask of the sig Zthrvol by the jubrain so that I can map the idx of
  # the voxels in Zthrvol for each of the regions inside the atlas
  Zatlas <- Zmask * jubrain
  
  
  # Find the index of the voxel belonging to each atlas region
  # Use one of the following two:
  
  # # (1) sapply version - pretty slow but already better than a normal loop
  # idx <- sapply(julabels$index, function(x) which(Zatlas == x))
  
  # (2) superfast parallel with foreach and %dopar%
  idx <- foreach(i = julabels$index) %dopar% {
    which(Zatlas == i)
  }
  
  # Calculate the stats to put in the table:
  # (1) numba voxels in each region
  julabels$nvox <- sapply(idx, length)
  
  # (2) mean Z value for the voxels in each region
  julabels$Zmean <- sapply(julabels$index, function(x) mean(Zthrvol[idx[x] %>% unlist]) )
  
  # (3) mean depth for the voxels in each region
  julabels$meanDepth <- sapply(julabels$index, function(x) mean(depth[idx[x] %>% unlist]) )
  
  # (4) std of depth
  julabels$stdDepth <- sapply(julabels$index, function(x) sd(depth[idx[x] %>% unlist]) )
  
  # (5) stdandard error of depth
  julabels$sderrDepth <- sapply(julabels$index, function(x) sderr(depth[idx[x] %>% unlist]) )
  
    
  # build the table to display
  tbl2display <- julabels %>%
    dplyr::select(-index) %>%
    filter(nvox > 200) %>%
    mutate(across(where(is.numeric), round, 2)) %>%
    arrange(desc(nvox))
  
  # write csv
  Zcontrast_name <- deparse(substitute(Zcontrast))
  write.csv(tbl2display, paste0(datadir,"/",Zcontrast_name,".csv"))
  
  return(tbl2display)
  
}






