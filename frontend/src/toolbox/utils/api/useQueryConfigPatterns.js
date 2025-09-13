
// const {
//   data,
//   dataUpdatedAt,
//   error,
//   errorUpdatedAt,
//   failureCount,
//   failureReason,
//   fetchStatus,
//   isError,
//   isFetched,
//   isFetchedAfterMount,
//   isFetching,
//   isInitialLoading,
//   isLoading,
//   isLoadingError,
//   isPaused,
//   isPending,
//   isPlaceholderData,
//   isRefetchError,
//   isRefetching,
//   isStale,
//   isSuccess,
//   isEnabled,
//   promise,
//   refetch,
//   status,
// } = useQuery(
//   {
//     queryKey,
//     queryFn,
//     gcTime,
//     enabled,
//     networkMode,
//     initialData,
//     initialDataUpdatedAt,
//     meta,
//     notifyOnChangeProps,
//     placeholderData,
//     queryKeyHashFn,
//     refetchInterval,
//     refetchIntervalInBackground,
//     refetchOnMount,
//     refetchOnReconnect,
//     refetchOnWindowFocus,
//     retry,
//     retryOnMount,
//     retryDelay,
//     select,
//     staleTime,
//     structuralSharing,
//     subscribed,
//     throwOnError,
//   },
//   queryClient,
// )

// NAMING CONVENTION:
// fetchTrigger                                   → manual (enabled: false - fetch manually), onMount (enabled: true - fetch on mount), realtime (enabled: true - runs repeatedly), onFocus (enabled: false - fetch on window focus)
// staleTime (for manual fetches)                 → instaOld (0 seconds) old5sec (5 seconds),  old1min (1 minute),  old5min (5 minutes), mummy (infinity)
// cacheTime [gcTime] (for manual and realtime)   → instaForget (0 seconds), cache5sec (5 seconds), cache1min (1 minute),  cache30min (30 minutes),  cacheForever (infinity) 
// retryTime                                      → notry (0 times, infinity delay), tryhard (infinity times every 3 seconds)

//manuals
export const manual_mummy_instaForget_notry = {
  enabled: false,
  refetchOnMount: false,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: Infinity,

  gcTime: 0,

  retry: 0,
  retryDelay: Infinity,
};


export const manual_mummy_cache1min_notry = {
  enabled: false,
  refetchOnMount: false,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: Infinity,

  gcTime: 60000,

  retry: 0,
  retryDelay: Infinity,
};

export const manual_mummy_cache30min_notry = {
  enabled: false,
  refetchOnMount: false,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: Infinity,

  gcTime: 60000*30,

  retry: 0,
  retryDelay: Infinity,
};

//on mount
export const onMount_instaOld_instaForget_notry = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 0,

  gcTime: 0,

  retry: 0,
  retryDelay: Infinity,
};

export const onMount_instaOld_cache1min_notry = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 0,

  gcTime: 60000,

  retry: 0,
  retryDelay: Infinity,
};

export const onMount_instaOld_cache30min_notry = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 0,

  gcTime: 60000*30,

  retry: 0,
  retryDelay: Infinity,
};

export const onMount_instaOld_cache30min_tryhard = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 0,

  gcTime: 60000*30,

  retry: Infinity,
  retryDelay: 3,
}; 

//on focus
export const onFocus_instaOld_instaForget_notry = {
  enabled: false,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: true,
  staleTime: 0,

  gcTime: 0,

  retry: 0,
  retryDelay: Infinity,
};

export const onFocus_instaOld_cache1min_notry = {
  enabled: false,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: true,
  staleTime: 0,

  gcTime: 60000,

  retry: 0,
  retryDelay: Infinity,
};

//realtime
export const realtime_old1min_cache1min_tryhard = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 60000,

  gcTime: 60000,

  retry: Infinity,
  retryDelay: 3000,
};

export const realtime_old30min_cache30min_tryhard = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 60000*30,

  gcTime: 60000*30,

  retry: Infinity,
  retryDelay: 3000,
};

export const realtime_instaOld_instaForget_tryhard = {
  enabled: true,
  refetchOnMount: true,
  refetchInterval: Infinity,

  refetchOnWindowFocus: false,
  staleTime: 0,

  gcTime: 0,

  retry: Infinity,
  retryDelay: 3000,
};

