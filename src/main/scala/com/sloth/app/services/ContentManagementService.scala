package com.sloth.app.services

import com.sloth.app.repositories.{AnalyticsRepository, MediaRepository, PostRepository, PostTaxonomiesRepository, TaxonomyRepository}

class ContentManagementService(
                              val postTaxonomiesRepository: PostTaxonomiesRepository = new PostTaxonomiesRepository,
                              val postRepository: PostRepository = new PostRepository,
                              val mediaRepository: MediaRepository = new MediaRepository,
                              val taxonomyRepository: TaxonomyRepository = new TaxonomyRepository,
                              val analyticsRepository: AnalyticsRepository = new AnalyticsRepository
                              ) {
  def deleteAllContent(): Boolean = {
    postTaxonomiesRepository.deleteAllPostTaxonomies()
    postRepository.deleteAllPosts()
    mediaRepository.deleteAllMedia()
    taxonomyRepository.deleteAllTaxonomy()
    analyticsRepository.deleteAnalyticsData()
    true
  }
}
