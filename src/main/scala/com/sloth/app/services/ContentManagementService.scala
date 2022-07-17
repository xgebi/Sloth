package com.sloth.app.services

import com.sloth.app.repositories.{AnalyticsRepository, MediaRepository, PostRepository, PostTaxonomiesRepository, TaxonomyRepository}

class ContentManagementService {
  def deleteAllContent(): Boolean = {
    (new PostTaxonomiesRepository).deleteAllPostTaxonomies()
    (new PostRepository).deleteAllPosts()
    (new MediaRepository).deleteAllMedia()
    (new TaxonomyRepository).deleteAllTaxonomy()
    (new AnalyticsRepository).deleteAnalyticsData()
    true
  }
}
