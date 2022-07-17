package com.sloth.app.services

import com.sloth.app.repositories.{AnalyticsRepository, MediaRepository, PostRepository, PostTaxonomiesRepository, TaxonomyRepository}
import org.scalamock.scalatest.MockFactory
import org.scalatest.funspec.AnyFunSpec
import org.scalatest.matchers.should.Matchers

class ContentManagementServiceTests extends AnyFunSpec with MockFactory with Matchers {

  describe("deleting all content") {
    it("should call several repositories") {
      val ptrMocked = mock[PostTaxonomiesRepository]
      val prMocked = mock[PostRepository]
      val mrMocked = mock[MediaRepository]
      val trMocked = mock[TaxonomyRepository]
      val arMocked = mock[AnalyticsRepository]

      (ptrMocked.deleteAllPostTaxonomies _).expects()
      (prMocked.deleteAllPosts _).expects()
      (mrMocked.deleteAllMedia _).expects()
      (trMocked.deleteAllTaxonomy _).expects()
      (arMocked.deleteAnalyticsData _).expects()

      val cms = new ContentManagementService(
        postTaxonomiesRepository = ptrMocked,
        postRepository = prMocked,
        mediaRepository = mrMocked,
        taxonomyRepository = trMocked,
        analyticsRepository = arMocked
      )
      cms.deleteAllContent().shouldBe(true)
    }
  }
}
